#!/usr/bin/env python3
"""
Simple prediction script for testing the trained diagonal parking classifier.
"""

import os
# Force CPU mode for consistency
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sys
import argparse
from pathlib import Path

def predict_single_image(model_path, image_path):
    """Predict diagonal parking for a single image."""
    try:
        import tensorflow as tf
        
        # Load the trained model
        print(f"Loading model from {model_path}...")
        model = tf.keras.models.load_model(model_path)
        
        # Load and preprocess the image
        print(f"Processing image: {image_path}")
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, axis=0) / 255.0
        
        # Make prediction
        prediction = model.predict(img_array, verbose=0)[0][0]
        # Note: diagonal_parking=0, no_diagonal_parking=1 based on training output
        predicted_class = "no_diagonal_parking" if prediction > 0.5 else "diagonal_parking"
        confidence = prediction if prediction > 0.5 else (1 - prediction)
        
        print(f"\n📋 Results for {Path(image_path).name}:")
        print(f"  Prediction: {predicted_class}")
        print(f"  Raw score: {prediction:.3f}")
        print(f"  Confidence: {confidence:.1%}")
        
        if predicted_class == "diagonal_parking":
            print("  ✅ Diagonal parking detected")
        else:
            print("  ❌ No diagonal parking detected")
            
        return prediction, predicted_class
        
    except Exception as e:
        print(f"❌ Error making prediction: {e}")
        return None, None

def predict_batch(model_path, image_dir, output_file=None):
    """Predict for all images in a directory."""
    image_dir = Path(image_dir)
    image_files = list(image_dir.glob("*.jpg"))
    
    if not image_files:
        print(f"❌ No .jpg images found in {image_dir}")
        return
    
    print(f"🔍 Found {len(image_files)} images to process")
    print("-" * 60)
    
    results = []
    positive_count = 0
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Processing {image_path.name}...")
        
        probability, predicted_class = predict_single_image(model_path, image_path)
        
        if probability is not None:
            results.append({
                'filename': image_path.name,
                'prediction': predicted_class,
                'probability': probability,
                'has_diagonal_parking': predicted_class == "diagonal_parking"
            })
            
            if predicted_class == "diagonal_parking":
                positive_count += 1
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"📊 Summary: {positive_count}/{len(image_files)} images contain diagonal parking")
    print(f"   Percentage: {positive_count/len(image_files)*100:.1f}%")
    
    # Save results to CSV if requested
    if output_file and results:
        import pandas as pd
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
        print(f"💾 Results saved to {output_file}")
    
    return results

def main():
    """Main prediction function."""
    parser = argparse.ArgumentParser(description="Predict diagonal parking in street view images")
    parser.add_argument("--model", required=True, help="Path to trained model (.h5 file)")
    parser.add_argument("--image", help="Path to single image to predict")
    parser.add_argument("--batch", help="Directory containing images to predict")
    parser.add_argument("--output", help="CSV file to save batch results")
    
    args = parser.parse_args()
    
    # Check if model exists
    if not Path(args.model).exists():
        print(f"❌ Model file not found: {args.model}")
        print("\nMake sure you've trained the model first:")
        print("  python train_model_cpu.py")
        sys.exit(1)
    
    if args.image:
        # Single image prediction
        if not Path(args.image).exists():
            print(f"❌ Image file not found: {args.image}")
            sys.exit(1)
        
        predict_single_image(args.model, args.image)
        
    elif args.batch:
        # Batch prediction
        if not Path(args.batch).exists():
            print(f"❌ Directory not found: {args.batch}")
            sys.exit(1)
        
        predict_batch(args.model, args.batch, args.output)
        
    else:
        print("❌ Please specify either --image or --batch")
        parser.print_help()
        
        # Show example usage
        print("\n📖 Example usage:")
        print("  # Single image:")
        print("  python predict_cpu.py --model diagonal_parking_classifier_cpu.h5 --image site_data/raw_images/orcutt_0001_h000_20250709_230749.jpg")
        print("")
        print("  # Batch prediction:")
        print("  python predict_cpu.py --model diagonal_parking_classifier_cpu.h5 --batch site_data/raw_images/ --output predictions.csv")

if __name__ == "__main__":
    main()
