#!/usr/bin/env python3
"""Local image-evidence and EV charging candidate dashboard.

Run with: python ui_server.py
The collector's Street View key is never sent to the browser.
"""

import argparse
import base64
import csv
import importlib.util
import io
import math
import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory
from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "2")
os.environ.setdefault("TF_NUM_INTEROP_THREADS", "2")
MODEL_PATH = ROOT / "site_data/model_checkpoints/best_model.h5"
# A single image at a time keeps MobileNet's activation memory bounded on CPUs.
BATCH_SIZE = 1


def load_catalog(root=ROOT):
    """Join actual, readable images to collector GPS metadata by filename."""
    paths, labels = {}, {}
    for split in ("train", "validation", "test"):
        for label in ("diagonal_parking", "no_diagonal_parking"):
            for path in (root / "site_data/processed_images" / split / label).glob("*"):
                if path.suffix.lower() in (".jpg", ".jpeg", ".png"):
                    paths[path.name] = path
                    labels[path.name] = label == "diagonal_parking"
    for path in (root / "site_data/raw_images").glob("*"):
        if path.suffix.lower() in (".jpg", ".jpeg", ".png"):
            paths[path.name] = path
    records = {}
    for metadata in sorted((root / "site_data/metadata").glob("*.csv")):
        with metadata.open(newline="") as handle:
            for row in csv.DictReader(handle):
                name = row.get("filename", "")
                if name not in paths or row.get("success", "").lower() != "true":
                    continue
                try:
                    lat, lon = float(row["latitude"]), float(row["longitude"])
                    heading = int(row["heading"])
                    if not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
                        continue
                except (KeyError, ValueError):
                    continue
                records[name] = {
                    "id": name, "filename": name, "path": paths[name],
                    "location_id": row["location_id"], "latitude": lat,
                    "longitude": lon, "heading": heading,
                    "timestamp": row.get("timestamp", ""),
                    "source": "label" if name in labels else "unreviewed",
                    "diagonal": labels.get(name), "probability": None,
                }
    return records


def public_record(record):
    return {**{key: value for key, value in record.items() if key != "path"},
            "image_url": f"/api/images/{record['id']}"}


def diagonal_probabilities(model, paths):
    """Match predict_cpu.py preprocessing and its class-0 diagonal mapping."""
    import numpy as np
    arrays = []
    for path in paths:
        with Image.open(path) as image:
            arrays.append(np.asarray(image.convert("RGB").resize((224, 224), Image.Resampling.NEAREST), dtype=np.float32) / 255.0)
    output = np.asarray(model(np.stack(arrays), training=False)).reshape(-1)
    if len(output) != len(paths) or not np.all(np.isfinite(output)) or np.any((output < 0) | (output > 1)):
        raise ValueError("The model returned invalid binary probabilities.")
    return [float(1 - value) for value in output]


def create_app(root=ROOT, predictor=None):
    app = Flask(__name__, static_folder=str(root / "ui"), static_url_path="/assets")
    app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024
    catalog = load_catalog(root)
    jobs = {}
    lock = threading.Lock()
    executor = ThreadPoolExecutor(max_workers=1)
    loaded_model = None

    # Only a deliberately configured browser key is exposed, never the collector key.
    browser_key = os.environ.get("GOOGLE_MAPS_BROWSER_API_KEY", "")
    try:
        from dotenv import dotenv_values
        browser_key = browser_key or dotenv_values(root / ".env").get("GOOGLE_MAPS_BROWSER_API_KEY", "") or ""
    except ImportError:
        pass

    @app.get("/")
    def index():
        return send_from_directory(root / "ui", "index.html")

    @app.get("/api/config")
    def config():
        return jsonify(maps_key=browser_key, model_available=bool(predictor or (MODEL_PATH.exists() and importlib.util.find_spec("tensorflow"))),
                       center={"lat": 34.865838, "lng": -120.447520})

    @app.get("/api/dataset")
    def dataset():
        with lock:
            return jsonify(images=[public_record(record) for record in catalog.values()])

    @app.get("/api/images/<image_id>")
    def image(image_id):
        with lock:
            record = catalog.get(image_id)
        if not record:
            return jsonify(error="Image not found."), 404
        return send_file(record["path"], max_age=3600)

    def run_analysis(job_id, records):
        nonlocal loaded_model
        try:
            if predictor is None and loaded_model is None:
                import tensorflow as tf
                loaded_model = tf.keras.models.load_model(MODEL_PATH, compile=False)
            results = []
            for offset in range(0, len(records), BATCH_SIZE):
                batch = records[offset:offset + BATCH_SIZE]
                paths = [record["path"] for record in batch]
                scores = predictor(paths) if predictor else diagonal_probabilities(loaded_model, paths)
                for record, score in zip(batch, scores):
                    results.append({**record, "probability": score, "diagonal": score >= 0.5, "source": "model"})
                with lock:
                    jobs[job_id]["completed"] = len(results)
            with lock:
                for record in results:
                    catalog[record["id"]] = record
                jobs[job_id].update(status="complete", images=[public_record(record) for record in results])
        except Exception as exc:
            app.logger.exception("Image analysis failed")
            with lock:
                jobs[job_id].update(status="error", error=f"Analysis failed ({type(exc).__name__}). Check the server terminal and model dependencies.")

    @app.post("/api/analyze")
    def analyze():
        payload = request.get_json(silent=True)
        if payload is None or not isinstance(payload, dict):
            return jsonify(error="Send a JSON object."), 400
        ids = payload.get("ids")
        if ids is not None and (not isinstance(ids, list) or not all(isinstance(value, str) for value in ids)):
            return jsonify(error="Image IDs must be a list of strings."), 400
        with lock:
            if any(job["status"] == "running" for job in jobs.values()):
                return jsonify(error="An analysis is already running. Wait for it to finish."), 409
            if ids is not None and any(image_id not in catalog for image_id in ids):
                return jsonify(error="An image ID was not found."), 400
            records = [dict(catalog[image_id]) for image_id in dict.fromkeys(ids)] if ids is not None else [dict(value) for value in catalog.values()]
            if not records:
                return jsonify(error="There are no images to analyze."), 400
            if predictor is None and (not MODEL_PATH.exists() or not importlib.util.find_spec("tensorflow")):
                return jsonify(error="Install TensorFlow and provide site_data/model_checkpoints/best_model.h5 to run analysis."), 503
            job_id = uuid.uuid4().hex
            jobs[job_id] = {"status": "running", "completed": 0, "total": len(records)}
            # Keep recent job results only; one running job is allowed.
            for old_id in list(jobs)[:-8]:
                del jobs[old_id]
        executor.submit(run_analysis, job_id, records)
        return jsonify(job_id=job_id), 202

    @app.get("/api/jobs/<job_id>")
    def job(job_id):
        with lock:
            result = jobs.get(job_id)
            return (jsonify(result), 200) if result else (jsonify(error="Job not found."), 404)

    @app.post("/api/uploads")
    def upload():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Send an image and its coordinates."), 400
        try:
            lat, lon = float(payload["latitude"]), float(payload["longitude"])
            if not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
                raise ValueError()
            raw = base64.b64decode(payload["data"], validate=True)
            if not raw or len(raw) > 8 * 1024 * 1024:
                raise ValueError()
            with Image.open(io.BytesIO(raw)) as incoming:
                if incoming.width * incoming.height > 25_000_000:
                    raise ValueError()
                incoming.verify()
            with Image.open(io.BytesIO(raw)) as incoming:
                output = incoming.convert("RGB")
                output.thumbnail((1600, 1600))
                image_id = f"upload_{uuid.uuid4().hex}.jpg"
                folder = root / "site_data/ui_uploads"
                folder.mkdir(parents=True, exist_ok=True)
                path = folder / image_id
                output.save(path, "JPEG", quality=90)
        except (KeyError, TypeError, ValueError, SyntaxError, UnidentifiedImageError, OSError, Image.DecompressionBombError):
            return jsonify(error="Use a valid image (up to 8 MB / 25 megapixels) and valid latitude and longitude."), 400
        with lock:
            # Reuse an existing location only for matching metadata coordinates.
            location_id = next((r["location_id"] for r in catalog.values() if abs(r["latitude"] - lat) < 1e-7 and abs(r["longitude"] - lon) < 1e-7), f"uploaded_{image_id[7:15]}")
            record = {"id": image_id, "filename": Path(str(payload.get("filename", "Uploaded image"))).name[:150], "path": path,
                      "latitude": lat, "longitude": lon, "location_id": location_id,
                      "heading": None, "timestamp": "", "source": "unreviewed", "probability": None, "diagonal": None}
            catalog[image_id] = record
        return jsonify(image=public_record(record)), 201

    @app.errorhandler(413)
    def too_large(_error):
        return jsonify(error="The upload is too large. Choose an image under 8 MB."), 413

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    create_app().run(host=args.host, port=args.port, threaded=True, debug=False)
