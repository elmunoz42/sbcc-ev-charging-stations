"""Checks for the image/GPS join, inference mapping, and upload boundaries."""

import base64
import csv
import io
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image

from ui_server import create_app, diagonal_probabilities, load_catalog


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        label_dir = self.root / 'site_data/processed_images/test/diagonal_parking'
        label_dir.mkdir(parents=True)
        self.image_path = label_dir / 'view.jpg'
        Image.new('RGB', (20, 20), (200, 100, 50)).save(self.image_path)
        metadata_dir = self.root / 'site_data/metadata'
        metadata_dir.mkdir(parents=True)
        with (metadata_dir / 'collection.csv').open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=['filename', 'success', 'location_id', 'latitude', 'longitude', 'heading'])
            writer.writeheader()
            writer.writerow(dict(filename='view.jpg', success=True, location_id='orcutt_0001', latitude=34.8, longitude=-120.4, heading=90))
            writer.writerow(dict(filename='missing.jpg', success=True, location_id='orcutt_0002', latitude=34.9, longitude=-120.5, heading=0))
        self.app = create_app(self.root, predictor=lambda paths: [0.85] * len(paths))
        self.client = self.app.test_client()

    def test_catalog_joins_only_available_images_and_preserves_labels(self):
        catalog = load_catalog(self.root)
        self.assertEqual(list(catalog), ['view.jpg'])
        record = catalog['view.jpg']
        self.assertTrue(record['diagonal'])
        self.assertIsNone(record['probability'])
        self.assertEqual(record['source'], 'label')
        self.assertEqual(record['latitude'], 34.8)

    def test_dataset_hides_paths_and_collector_secrets(self):
        (self.root / '.env').write_text('google_maps_street_view_api=server-secret\n')
        with patch.dict('os.environ', {'GOOGLE_MAPS_BROWSER_API_KEY': ''}):
            client = create_app(self.root, predictor=lambda paths: []).test_client()
            self.assertEqual(client.get('/api/config').json['maps_key'], '')
        data = self.client.get('/api/dataset').json['images'][0]
        self.assertNotIn('path', data)
        with self.client.get(data['image_url']) as response:
            self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/api/images/missing.jpg').status_code, 404)

    def test_model_class_zero_mapping_and_preprocessing(self):
        def fake_model(batch, training):
            self.assertEqual(batch.shape, (1, 224, 224, 3))
            self.assertEqual(batch.dtype, np.float32)
            self.assertGreaterEqual(batch.min(), 0)
            self.assertLessEqual(batch.max(), 1)
            self.assertFalse(training)
            return np.array([[0.2]])
        self.assertAlmostEqual(diagonal_probabilities(fake_model, [self.image_path])[0], 0.8)

    def test_model_rejects_invalid_probability(self):
        with self.assertRaises(ValueError):
            diagonal_probabilities(lambda batch, training: np.array([[np.nan]]), [self.image_path])

    def wait_for_job(self, job_id):
        for _ in range(100):
            job = self.client.get(f'/api/jobs/{job_id}').json
            if job['status'] != 'running':
                return job
            time.sleep(0.01)
        self.fail('Background analysis did not finish')

    def test_analysis_replaces_label_with_model_result(self):
        response = self.client.post('/api/analyze', json={})
        self.assertEqual(response.status_code, 202)
        job = self.wait_for_job(response.json['job_id'])
        self.assertEqual(job['status'], 'complete')
        self.assertEqual(job['completed'], 1)
        image = self.client.get('/api/dataset').json['images'][0]
        self.assertEqual(image['source'], 'model')
        self.assertEqual(image['probability'], 0.85)
        self.assertTrue(image['diagonal'])

    def test_invalid_analysis_ids_are_rejected(self):
        for payload in ({'ids': ['missing']}, {'ids': 'view.jpg'}, {'ids': []}, []):
            self.assertEqual(self.client.post('/api/analyze', json=payload).status_code, 400)

    def upload_payload(self):
        image = io.BytesIO()
        Image.new('RGB', (10, 10), 'green').save(image, 'PNG')
        return dict(data=base64.b64encode(image.getvalue()).decode(), filename='../../photo.png', latitude=34.8, longitude=-120.4)

    def test_upload_preserves_coordinates_without_inventing_predictions(self):
        response = self.client.post('/api/uploads', json=self.upload_payload())
        self.assertEqual(response.status_code, 201)
        image = response.json['image']
        self.assertEqual(image['location_id'], 'orcutt_0001')
        self.assertEqual(image['filename'], 'photo.png')
        self.assertEqual(image['latitude'], 34.8)
        self.assertIsNone(image['probability'])
        self.assertIsNone(image['diagonal'])
        self.assertEqual(image['source'], 'unreviewed')
        with self.client.get(image['image_url']) as response:
            self.assertEqual(response.status_code, 200)
        start = self.client.post('/api/analyze', json={'ids': [image['id']]})
        self.assertEqual(self.wait_for_job(start.json['job_id'])['total'], 1)

    def test_bad_upload_data_and_coordinates_are_rejected(self):
        corrupt_png = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a1ioAAAAASUVORK5CYII='
        for changes in ({'latitude': 91}, {'longitude': -181}, {'latitude': 'nan'}, {'data': 'not base64!'}, {'data': base64.b64encode(b'not an image').decode()}, {'data': corrupt_png}):
            payload = {**self.upload_payload(), **changes}
            self.assertEqual(self.client.post('/api/uploads', json=payload).status_code, 400)


if __name__ == '__main__':
    unittest.main()
