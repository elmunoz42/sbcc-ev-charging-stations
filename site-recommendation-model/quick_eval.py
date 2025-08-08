#!/usr/bin/env python3
"""
Quick evaluation script for the diagonal parking classifier
"""

import os
import glob
import subprocess
import json

def run_prediction(model_path, image_path):
    """Run prediction on a single image"""
    try:
        result = subprocess.run([
            'python', 'predict_cpu.py', 
            '--model', model_path,
            '--image', image_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse the output to extract prediction
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'Prediction:' in line:
                    prediction = line.split('Prediction:')[1].strip()
                    return prediction
        return None
    except Exception as e:
        print(f"Error predicting {image_path}: {e}")
        return None

def main():
    model_path = 'site_data/model_checkpoints/best_model.h5'
    
    # Test images from each category
    diagonal_files = glob.glob('site_data/processed_images/test/diagonal_parking/*.jpg')[:3]
    no_diagonal_files = glob.glob('site_data/processed_images/test/no_diagonal_parking/*.jpg')[:3]
    
    print("Diagonal Parking Test Images:")
    print("=" * 50)
    diagonal_correct = 0
    for img_path in diagonal_files:
        prediction = run_prediction(model_path, img_path)
        filename = os.path.basename(img_path)
        correct = prediction == 'diagonal_parking'
        if correct:
            diagonal_correct += 1
        print(f"{filename:40} | {prediction:20} | {'✓' if correct else '✗'}")
    
    print(f"\nNo Diagonal Parking Test Images:")
    print("=" * 50)
    no_diagonal_correct = 0
    for img_path in no_diagonal_files:
        prediction = run_prediction(model_path, img_path)
        filename = os.path.basename(img_path)
        correct = prediction == 'no_diagonal_parking'
        if correct:
            no_diagonal_correct += 1
        print(f"{filename:40} | {prediction:20} | {'✓' if correct else '✗'}")
    
    print(f"\nSummary:")
    print(f"Diagonal parking accuracy: {diagonal_correct}/{len(diagonal_files)} ({diagonal_correct/len(diagonal_files)*100:.1f}%)")
    print(f"No diagonal parking accuracy: {no_diagonal_correct}/{len(no_diagonal_files)} ({no_diagonal_correct/len(no_diagonal_files)*100:.1f}%)")
    print(f"Overall accuracy: {(diagonal_correct + no_diagonal_correct)}/{(len(diagonal_files) + len(no_diagonal_files))} ({(diagonal_correct + no_diagonal_correct)/(len(diagonal_files) + len(no_diagonal_files))*100:.1f}%)")

if __name__ == "__main__":
    main()
