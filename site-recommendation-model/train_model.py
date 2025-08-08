#!/usr/bin/env python3
"""
Simple training script for the diagonal parking classifier.
Run this script to train the model on your labeled data.
"""

import os
import sys
from pathlib import Path

def check_data_structure():
    """Check if the data is properly organized."""
    required_dirs = [
        "site_data/processed_images/train/diagonal_parking",
        "site_data/processed_images/train/no_diagonal_parking", 
        "site_data/processed_images/test/diagonal_parking",
        "site_data/processed_images/test/no_diagonal_parking"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing required directories:")
        for dir_path in missing_dirs:
            print(f"   {dir_path}")
        print("\nPlease organize your images into the required folder structure.")
        return False
    
    # Count images in each directory
    for dir_path in required_dirs:
        image_count = len(list(Path(dir_path).glob("*.jpg")))
        print(f"✓ {dir_path}: {image_count} images")
    
    return True

def main():
    """Main training function."""
    print("Diagonal Parking Classifier Training")
    print("=" * 40)
    
    # Check data structure
    if not check_data_structure():
        return
    
    try:
        # Import the classifier (will show import errors if dependencies missing)
        from diagonal_parking_classifier import DiagonalParkingClassifier
        print("✓ Dependencies loaded successfully")
        
        # Initialize and train
        print("\nInitializing classifier...")
        classifier = DiagonalParkingClassifier()
        
        print("Creating data generators...")
        train_gen, val_gen, test_gen = classifier.create_data_generators()
        
        print("Building model...")
        model = classifier.create_model()
        
        print("\nModel Summary:")
        model.summary()
        
        # Ask user if they want to proceed
        response = input("\nProceed with training? (y/n): ").lower().strip()
        if response != 'y':
            print("Training cancelled.")
            return
        
        print("\nStarting training...")
        print("This may take 10-30 minutes depending on your GPU.")
        
        # Train the model
        classifier.train_model(train_gen, val_gen, epochs=50)
        classifier.fine_tune_model(train_gen, val_gen, epochs=30)
        
        # Evaluate
        print("\nEvaluating model...")
        results = classifier.evaluate_model(test_gen)
        
        # Save results
        classifier.plot_training_history(save_path="training_history.png")
        model_path = classifier.save_model()
        
        print("\n🎉 Training completed successfully!")
        print(f"Model saved to: {model_path}")
        print(f"Training plot saved to: training_history.png")
        
        print(f"\nFinal Results:")
        print(f"  Test Accuracy: {results['test_accuracy']:.3f}")
        print(f"  Test Precision: {results['test_precision']:.3f}")
        print(f"  Test Recall: {results['test_recall']:.3f}")
        print(f"  Test F1-Score: {results['test_f1_score']:.3f}")
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("\nPlease install required packages:")
        print("pip install tensorflow numpy matplotlib scikit-learn")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
