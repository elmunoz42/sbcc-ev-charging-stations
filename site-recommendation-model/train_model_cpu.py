#!/usr/bin/env python3
"""
CPU-only training script for the diagonal parking classifier.
This version avoids all GPU/CUDA issues and trains reliably on CPU.
"""

import os
# Force CPU-only training to avoid CUDA libdevice issues
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TensorFlow warnings

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
    total_train = 0
    total_test = 0
    
    for dir_path in required_dirs:
        image_count = len(list(Path(dir_path).glob("*.jpg")))
        print(f"✓ {dir_path}: {image_count} images")
        
        if "train" in dir_path:
            total_train += image_count
        else:
            total_test += image_count
    
    print(f"\nTotal training images: {total_train}")
    print(f"Total test images: {total_test}")
    
    return True

def main():
    """Main training function."""
    print("Diagonal Parking Classifier Training (CPU Mode)")
    print("=" * 50)
    
    # Check data structure
    if not check_data_structure():
        return False
    
    try:
        # Import the classifier
        from diagonal_parking_classifier import DiagonalParkingClassifier
        print("✓ Dependencies loaded successfully")
        
        # Initialize classifier (disable mixed precision for CPU)
        print("\nInitializing classifier for CPU training...")
        classifier = DiagonalParkingClassifier()
        
        # Override mixed precision setup for CPU
        classifier._setup_mixed_precision = lambda: None
        
        print("Creating data generators...")
        train_gen, val_gen, test_gen = classifier.create_data_generators()
        
        print("Building model...")
        model = classifier.create_model()
        
        # Recompile model without mixed precision
        import tensorflow as tf
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        print("\nModel Summary:")
        model.summary()
        
        print(f"\nDataset Summary:")
        print(f"  Training samples: {train_gen.samples}")
        print(f"  Validation samples: {val_gen.samples}")
        print(f"  Test samples: {test_gen.samples}")
        print(f"  Classes: {train_gen.class_indices}")
        
        # Ask user if they want to proceed
        response = input("\nProceed with CPU training? (y/n): ").lower().strip()
        if response != 'y':
            print("Training cancelled.")
            return False
        
        print("\nStarting CPU training...")
        print("Expected time: 20-30 minutes")
        print("The model will train for up to 30 epochs with early stopping.")
        
        # Train the model with fewer epochs for CPU
        print("\nPhase 1: Initial training with frozen base layers...")
        classifier.train_model(train_gen, val_gen, epochs=30)
        
        print("\nPhase 2: Fine-tuning with unfrozen layers...")
        classifier.fine_tune_model(train_gen, val_gen, epochs=20)
        
        # Evaluate
        print("\nEvaluating model on test set...")
        results = classifier.evaluate_model(test_gen)
        
        # Save results
        print("\nSaving results...")
        plot_path = "training_history_cpu.png"
        classifier.plot_training_history(save_path=plot_path)
        
        model_path = "diagonal_parking_classifier_cpu.h5"
        classifier.model.save(model_path)
        
        print("\n🎉 Training completed successfully!")
        print(f"✓ Model saved as: {model_path}")
        print(f"✓ Training plot saved as: {plot_path}")
        
        print(f"\n📊 Final Results:")
        print(f"  Test Accuracy:  {results['test_accuracy']:.3f}")
        print(f"  Test Precision: {results['test_precision']:.3f}")
        print(f"  Test Recall:    {results['test_recall']:.3f}")
        print(f"  Test F1-Score:  {results['test_f1_score']:.3f}")
        
        # Provide interpretation
        print(f"\n📈 Model Performance Analysis:")
        if results['test_accuracy'] > 0.85:
            print("  🟢 Excellent accuracy! Model performs very well.")
        elif results['test_accuracy'] > 0.75:
            print("  🟡 Good accuracy. Model is reasonably reliable.")
        else:
            print("  🔴 Moderate accuracy. Consider more training data.")
            
        if results['test_precision'] > 0.8:
            print("  🟢 High precision: Low false positive rate.")
        else:
            print("  🟡 Moderate precision: Some false positives expected.")
            
        if results['test_recall'] > 0.7:
            print("  🟢 Good recall: Catches most diagonal parking cases.")
        else:
            print("  🟡 Moderate recall: May miss some diagonal parking cases.")
        
        print(f"\n🚀 Next Steps:")
        print(f"  1. Test the model: python predict.py --model {model_path} --image path/to/image.jpg")
        print(f"  2. Batch predict: python predict.py --model {model_path} --batch site_data/raw_images/")
        print(f"  3. Review training plots in {plot_path}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("\nPlease install required packages:")
        print("conda activate ev_model")
        print("pip install tensorflow numpy matplotlib scikit-learn pillow")
        return False
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ CPU training completed successfully!")
    else:
        print("\n❌ CPU training failed.")
    
    sys.exit(0 if success else 1)
