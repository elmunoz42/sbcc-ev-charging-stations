#!/usr/bin/env python3
"""
Prediction script for testing the trained diagonal parking classifier on individual images.
"""

import argparse
import sys
from pathlib import Path

def predict_single_image(model_path, image_path):
    """Predict diagonal parking for a single image."""
    try:
        from diagonal_parking_classifier import DiagonalParkingClassifier
        import tensorflow as tf
        
        # Load the trained model
        classifier = DiagonalParkingClassifier()
        classifier.model = tf.keras.models.load_model(model_path)
        
        # Make prediction
        probability, predicted_class = classifier.predict_image(image_path)
        
        print(f"Image: {image_path}")
        print(f"Prediction: {predicted_class}")
        print(f"Confidence: {probability:.3f}")
        
        if predicted_class == "diagonal_parking":
            print("✓ Diagonal parking detected")
        else:
            print("✗ No diagonal parking detected")
            
        return probability, predicted_class
        
    except Exception as e:
        print(f"Error making prediction: {e}")
        return None, None

def predict_batch(model_path, image_dir):
    """Predict for all images in a directory."""
    image_dir = Path(image_dir)
    image_files = list(image_dir.glob("*.jpg"))
    
    if not image_files:
        print(f"No .jpg images found in {image_dir}")
        return
    
    print(f"Found {len(image_files)} images to process")
    print("-" * 50)
    
    positive_count = 0
    
    for image_path in image_files:
        probability, predicted_class = predict_single_image(model_path, image_path)
        
        if predicted_class == "diagonal_parking":
            positive_count += 1
        
        print()  # Add spacing between predictions
    
    print(f"Summary: {positive_count}/{len(image_files)} images contain diagonal parking")

def main():
    """Main prediction function."""
    parser = argparse.ArgumentParser(description="Predict diagonal parking in street view images")
    parser.add_argument("--model", required=True, help="Path to trained model (.h5 file)")
    parser.add_argument("--image", help="Path to single image to predict")
    parser.add_argument("--batch", help="Directory containing images to predict")
    
    args = parser.parse_args()
    
    # Check if model exists
    if not Path(args.model).exists():
        print(f"Model file not found: {args.model}")
        sys.exit(1)
    
    if args.image:
        # Single image prediction
        if not Path(args.image).exists():
            print(f"Image file not found: {args.image}")
            sys.exit(1)
        
        predict_single_image(args.model, args.image)
        
    elif args.batch:
        # Batch prediction
        if not Path(args.batch).exists():
            print(f"Directory not found: {args.batch}")
            sys.exit(1)
        
        predict_batch(args.model, args.batch)
        
    else:
        print("Please specify either --image or --batch")
        parser.print_help()

if __name__ == "__main__":
    main()
