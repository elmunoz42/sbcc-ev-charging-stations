#!/usr/bin/env python3
"""
Diagonal Parking Classifier using Transfer Learning
Trains a model to identify diagonal parking in street view images for EV charging station placement.

This model uses:
- Pre-trained MobileNetV2 for transfer learning (efficient for small datasets)
- Heavy data augmentation to handle limited training data
- Mixed precision training for GPU efficiency
- Early stopping and model checkpointing
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiagonalParkingClassifier:
    def __init__(self, base_dir="site_data", img_height=224, img_width=224):
        """
        Initialize the diagonal parking classifier.
        
        Args:
            base_dir: Base directory containing processed_images folder
            img_height: Target image height for training
            img_width: Target image width for training
        """
        self.base_dir = Path(base_dir)
        self.img_height = img_height
        self.img_width = img_width
        self.batch_size = 16  # Small batch size for limited data
        
        # Paths
        self.train_dir = self.base_dir / "processed_images" / "train"
        self.test_dir = self.base_dir / "processed_images" / "test"
        
        # Model components
        self.model = None
        self.history = None
        
        # Check GPU availability
        self._check_gpu()
        
        # Enable mixed precision for better GPU performance
        self._setup_mixed_precision()
    
    def _check_gpu(self):
        """Check GPU availability and configuration."""
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                # Enable memory growth to avoid allocating all GPU memory at once
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logger.info(f"Found {len(gpus)} GPU(s): {[gpu.name for gpu in gpus]}")
            except RuntimeError as e:
                logger.error(f"GPU configuration error: {e}")
        else:
            logger.warning("No GPU found. Training will use CPU (slower).")
    
    def _setup_mixed_precision(self):
        """Setup mixed precision training for better GPU performance."""
        policy = tf.keras.mixed_precision.Policy('mixed_float16')
        tf.keras.mixed_precision.set_global_policy(policy)
        logger.info("Mixed precision training enabled")
    
    def create_data_generators(self):
        """
        Create data generators with heavy augmentation for small dataset.
        
        Returns:
            tuple: (train_generator, validation_generator, test_generator)
        """
        # Heavy augmentation for training data (small dataset needs this)
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=30,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            vertical_flip=False,  # Don't flip vertically for street views
            brightness_range=[0.8, 1.2],
            channel_shift_range=0.1,
            fill_mode='nearest',
            validation_split=0.2  # Use 20% of training data for validation
        )
        
        # Minimal augmentation for validation (from training split)
        validation_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=0.2
        )
        
        # No augmentation for test data
        test_datagen = ImageDataGenerator(rescale=1./255)
        
        # Training generator
        train_generator = train_datagen.flow_from_directory(
            self.train_dir,
            target_size=(self.img_height, self.img_width),
            batch_size=self.batch_size,
            class_mode='binary',
            subset='training',
            seed=42
        )
        
        # Validation generator (from training data split)
        validation_generator = validation_datagen.flow_from_directory(
            self.train_dir,
            target_size=(self.img_height, self.img_width),
            batch_size=self.batch_size,
            class_mode='binary',
            subset='validation',
            seed=42
        )
        
        # Test generator
        test_generator = test_datagen.flow_from_directory(
            self.test_dir,
            target_size=(self.img_height, self.img_width),
            batch_size=self.batch_size,
            class_mode='binary',
            shuffle=False
        )
        
        logger.info(f"Training samples: {train_generator.samples}")
        logger.info(f"Validation samples: {validation_generator.samples}")
        logger.info(f"Test samples: {test_generator.samples}")
        logger.info(f"Classes: {train_generator.class_indices}")
        
        return train_generator, validation_generator, test_generator
    
    def create_model(self):
        """
        Create transfer learning model using pre-trained MobileNetV2.
        MobileNetV2 is chosen for efficiency and good performance on small datasets.
        """
        # Load pre-trained MobileNetV2 (without top classification layer)
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=(self.img_height, self.img_width, 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze the base model initially
        base_model.trainable = False
        
        # Add custom classification head
        model = tf.keras.Sequential([
            base_model,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.5),  # High dropout for small dataset
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(1, activation='sigmoid', dtype='float32')  # float32 for stability
        ])
        
        # Compile with appropriate loss for binary classification
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        self.model = model
        logger.info("Model created with transfer learning")
        logger.info(f"Total parameters: {model.count_params():,}")
        logger.info(f"Trainable parameters: {sum([tf.keras.backend.count_params(w) for w in model.trainable_weights]):,}")
        
        return model
    
    def train_model(self, train_generator, validation_generator, epochs=50):
        """
        Train the model with callbacks for early stopping and checkpointing.
        
        Args:
            train_generator: Training data generator
            validation_generator: Validation data generator
            epochs: Maximum number of epochs
        """
        # Create model checkpoint directory
        checkpoint_dir = self.base_dir / "model_checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)
        
        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            tf.keras.callbacks.ModelCheckpoint(
                checkpoint_dir / "best_model.h5",
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            )
        ]
        
        # Train the model
        logger.info("Starting initial training (frozen base model)...")
        self.history = self.model.fit(
            train_generator,
            epochs=epochs,
            validation_data=validation_generator,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("Initial training completed")
        return self.history
    
    def fine_tune_model(self, train_generator, validation_generator, epochs=30):
        """
        Fine-tune the model by unfreezing some layers of the base model.
        
        Args:
            train_generator: Training data generator
            validation_generator: Validation data generator
            epochs: Number of fine-tuning epochs
        """
        # Unfreeze the last few layers of the base model
        base_model = self.model.layers[0]
        base_model.trainable = True
        
        # Fine-tune from this layer onwards
        fine_tune_at = len(base_model.layers) - 20
        
        # Freeze all layers before fine_tune_at
        for layer in base_model.layers[:fine_tune_at]:
            layer.trainable = False
        
        # Recompile with lower learning rate for fine-tuning
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001/10),  # Lower LR
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        logger.info(f"Fine-tuning from layer {fine_tune_at} onwards")
        logger.info(f"Trainable parameters: {sum([tf.keras.backend.count_params(w) for w in self.model.trainable_weights]):,}")
        
        # Continue training with fine-tuning
        fine_tune_history = self.model.fit(
            train_generator,
            epochs=epochs,
            validation_data=validation_generator,
            initial_epoch=len(self.history.history['loss']),
            verbose=1
        )
        
        # Combine histories
        for key in self.history.history.keys():
            if key in fine_tune_history.history:
                self.history.history[key].extend(fine_tune_history.history[key])
        
        logger.info("Fine-tuning completed")
    
    def evaluate_model(self, test_generator):
        """
        Evaluate the model on test data.
        
        Args:
            test_generator: Test data generator
            
        Returns:
            dict: Evaluation metrics
        """
        # Evaluate
        test_loss, test_accuracy, test_precision, test_recall = self.model.evaluate(
            test_generator, 
            verbose=1
        )
        
        # Calculate F1 score
        f1_score = 2 * (test_precision * test_recall) / (test_precision + test_recall + 1e-7)
        
        results = {
            'test_loss': test_loss,
            'test_accuracy': test_accuracy,
            'test_precision': test_precision,
            'test_recall': test_recall,
            'test_f1_score': f1_score
        }
        
        logger.info("Model Evaluation Results:")
        for metric, value in results.items():
            logger.info(f"  {metric}: {value:.4f}")
        
        return results
    
    def plot_training_history(self, save_path=None):
        """
        Plot training history.
        
        Args:
            save_path: Path to save the plot
        """
        if self.history is None:
            logger.error("No training history found. Train the model first.")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Accuracy
        axes[0, 0].plot(self.history.history['accuracy'], label='Training Accuracy')
        axes[0, 0].plot(self.history.history['val_accuracy'], label='Validation Accuracy')
        axes[0, 0].set_title('Model Accuracy')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        
        # Loss
        axes[0, 1].plot(self.history.history['loss'], label='Training Loss')
        axes[0, 1].plot(self.history.history['val_loss'], label='Validation Loss')
        axes[0, 1].set_title('Model Loss')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        
        # Precision
        axes[1, 0].plot(self.history.history['precision'], label='Training Precision')
        axes[1, 0].plot(self.history.history['val_precision'], label='Validation Precision')
        axes[1, 0].set_title('Model Precision')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Precision')
        axes[1, 0].legend()
        
        # Recall
        axes[1, 1].plot(self.history.history['recall'], label='Training Recall')
        axes[1, 1].plot(self.history.history['val_recall'], label='Validation Recall')
        axes[1, 1].set_title('Model Recall')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Recall')
        axes[1, 1].legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Training history plot saved to {save_path}")
        
        plt.show()
    
    def save_model(self, model_path=None):
        """
        Save the trained model.
        
        Args:
            model_path: Path to save the model
        """
        if self.model is None:
            logger.error("No model found. Train the model first.")
            return
        
        if model_path is None:
            model_path = self.base_dir / f"diagonal_parking_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
        
        self.model.save(model_path)
        logger.info(f"Model saved to {model_path}")
        
        return model_path
    
    def predict_image(self, image_path):
        """
        Predict diagonal parking for a single image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            tuple: (prediction_probability, predicted_class)
        """
        if self.model is None:
            logger.error("No model found. Train the model first.")
            return None, None
        
        # Load and preprocess image
        img = tf.keras.preprocessing.image.load_img(
            image_path, 
            target_size=(self.img_height, self.img_width)
        )
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        
        # Predict
        prediction = self.model.predict(img_array, verbose=0)[0][0]
        predicted_class = "diagonal_parking" if prediction > 0.5 else "no_diagonal_parking"
        
        return float(prediction), predicted_class


def main():
    """Main function to train the diagonal parking classifier."""
    logger.info("Starting Diagonal Parking Classifier Training")
    
    # Initialize classifier
    classifier = DiagonalParkingClassifier()
    
    # Create data generators
    train_gen, val_gen, test_gen = classifier.create_data_generators()
    
    # Create model
    model = classifier.create_model()
    
    # Print model summary
    model.summary()
    
    # Train model
    logger.info("Phase 1: Initial training with frozen base model")
    classifier.train_model(train_gen, val_gen, epochs=50)
    
    # Fine-tune model
    logger.info("Phase 2: Fine-tuning with unfrozen layers")
    classifier.fine_tune_model(train_gen, val_gen, epochs=30)
    
    # Evaluate model
    logger.info("Evaluating model on test set")
    results = classifier.evaluate_model(test_gen)
    
    # Plot training history
    plot_path = classifier.base_dir / "training_history.png"
    classifier.plot_training_history(save_path=plot_path)
    
    # Save model
    model_path = classifier.save_model()
    
    logger.info("Training completed successfully!")
    logger.info(f"Model saved to: {model_path}")
    logger.info(f"Training plot saved to: {plot_path}")
    
    return classifier, results


if __name__ == "__main__":
    # Set up tensorflow logging
    tf.get_logger().setLevel('INFO')
    
    # Run training
    classifier, results = main()
