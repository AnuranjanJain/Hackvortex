"""
SewageMapAI - U-Net Neural Network Model
========================================

This file contains the AI brain of SewageMapAI. It uses a U-Net convolutional 
neural network to analyze satellite images and detect sewage infrastructure.

What is U-Net?
- U-Net is a type of neural network designed for image segmentation
- It can identify specific objects or patterns in images pixel by pixel
- Originally designed for medical imaging, adapted here for sewage detection

How it works:
1. Takes a satellite image as input
2. Compresses it down through encoder layers (finding features)
3. Expands it back up through decoder layers (creating predictions)
4. Outputs a mask showing where sewage lines are detected

Author: SewageMapAI Team
Optimized for: Various GPUs including RTX 3050, also works on CPU
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import cv2
import os
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class UNetSewageSegmentation:
    """
    U-Net Neural Network for Sewage Detection
    
    This class implements a U-Net architecture specifically designed
    to detect sewage infrastructure in satellite images.
    """
    
    def __init__(self, input_size=(128, 128, 3)):
        """
        Initialize the U-Net model
        
        Args:
            input_size: Image dimensions (height, width, channels)
                       Default: 128x128 RGB images for optimal performance
        """
        self.input_size = input_size
        self.model = None
        self.model_path = os.path.join('models', 'sewage_ai_model.h5')
        
    def build_unet(self):
        """
        Build the U-Net neural network architecture
        
        The network has:
        - Encoder: Compresses image to find features (32→64→128→256 filters)
        - Bridge: Processes the most compressed features (256 filters)
        - Decoder: Expands back to full image size (128→64→32 filters)
        - Output: Single channel mask showing sewage locations
        
        Returns:
            Compiled Keras model ready for training
        """
        inputs = keras.Input(shape=self.input_size)
        
        # ENCODER PATH (Contracting - finds features)
        # Layer 1: Initial feature detection
        conv1 = layers.Conv2D(32, 3, activation='relu', padding='same')(inputs)
        conv1 = layers.Dropout(0.1)(conv1)
        conv1 = layers.Conv2D(32, 3, activation='relu', padding='same')(conv1)
        pool1 = layers.MaxPooling2D(pool_size=(2, 2))(conv1)
        
        # Layer 2: More complex features
        conv2 = layers.Conv2D(64, 3, activation='relu', padding='same')(pool1)
        conv2 = layers.Dropout(0.1)(conv2)
        conv2 = layers.Conv2D(64, 3, activation='relu', padding='same')(conv2)
        pool2 = layers.MaxPooling2D(pool_size=(2, 2))(conv2)
        
        # Layer 3: High-level features
        conv3 = layers.Conv2D(128, 3, activation='relu', padding='same')(pool2)
        conv3 = layers.Dropout(0.2)(conv3)
        conv3 = layers.Conv2D(128, 3, activation='relu', padding='same')(conv3)
        pool3 = layers.MaxPooling2D(pool_size=(2, 2))(conv3)
        
        # BRIDGE: Deepest layer (bottleneck)
        conv4 = layers.Conv2D(256, 3, activation='relu', padding='same')(pool3)
        conv4 = layers.Dropout(0.3)(conv4)
        conv4 = layers.Conv2D(256, 3, activation='relu', padding='same')(conv4)
        
        # DECODER PATH (Expanding - creates predictions)
        # Layer 5: Start expanding + combine with layer 3
        up5 = layers.Conv2DTranspose(128, 2, strides=(2, 2), padding='same')(conv4)
        up5 = layers.concatenate([up5, conv3])
        conv5 = layers.Conv2D(128, 3, activation='relu', padding='same')(up5)
        conv5 = layers.Dropout(0.2)(conv5)
        conv5 = layers.Conv2D(128, 3, activation='relu', padding='same')(conv5)
        
        # Layer 6: Continue expanding + combine with layer 2
        up6 = layers.Conv2DTranspose(64, 2, strides=(2, 2), padding='same')(conv5)
        up6 = layers.concatenate([up6, conv2])
        conv6 = layers.Conv2D(64, 3, activation='relu', padding='same')(up6)
        conv6 = layers.Dropout(0.1)(conv6)
        conv6 = layers.Conv2D(64, 3, activation='relu', padding='same')(conv6)
        
        # Layer 7: Final expansion + combine with layer 1
        up7 = layers.Conv2DTranspose(32, 2, strides=(2, 2), padding='same')(conv6)
        up7 = layers.concatenate([up7, conv1])
        conv7 = layers.Conv2D(32, 3, activation='relu', padding='same')(up7)
        conv7 = layers.Dropout(0.1)(conv7)
        conv7 = layers.Conv2D(32, 3, activation='relu', padding='same')(conv7)
        
        # OUTPUT: Final prediction layer
        outputs = layers.Conv2D(1, 1, activation='sigmoid')(conv7)
        
        model = keras.Model(inputs=[inputs], outputs=[outputs])
        return model
    
    def compile_model(self):
        """
        Compile the model with appropriate settings for sewage detection
        
        Uses:
        - Adam optimizer with learning rate 0.0001 (stable training)
        - Binary crossentropy loss (good for binary masks)
        - Accuracy and IoU metrics for monitoring
        """
        if self.model is None:
            self.model = self.build_unet()
        
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'iou']
        )    
    def load_model(self):
        """
        Load a previously trained model from disk
        
        Returns:
            bool: True if model loaded successfully, False if no saved model found
        """
        try:
            if os.path.exists(self.model_path):
                self.model = keras.models.load_model(self.model_path)
                logger.info(f"Pre-trained AI model loaded from {self.model_path}")
                return True
            else:
                logger.info("No pre-trained model found, will need to train from scratch")
                return False
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def save_model(self):
        """Save the trained model to disk for future use"""
        try:
            if self.model is not None:
                # Make sure directory exists
                model_dir = os.path.dirname(self.model_path)
                if not os.path.exists(model_dir):
                    os.makedirs(model_dir, exist_ok=True)
                self.model.save(self.model_path)
                logger.info(f"AI model saved successfully to {self.model_path}")
            else:
                logger.error("No model to save")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
    
    def preprocess_image(self, image_path, target_size=(128, 128)):
        """
        Prepare an image for AI analysis
        
        Steps:
        1. Load image from file
        2. Convert color format (BGR → RGB)
        3. Resize to standard size (128x128)
        4. Normalize pixel values (0-255 → 0-1)
        5. Add batch dimension for neural network
        
        Args:
            image_path: Path to the image file
            target_size: Size to resize image to
            
        Returns:
            Preprocessed image ready for AI prediction
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not load image - check file path and format")
            
            # Convert BGR (OpenCV) to RGB (standard)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize to standard size
            image = cv2.resize(image, target_size)
            
            # Normalize to 0-1 range (neural networks work better this way)
            image = image.astype(np.float32) / 255.0
            
            # Add batch dimension (neural networks expect batches)
            image = np.expand_dims(image, axis=0)
            
            return image
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise
    
    def predict(self, image_path, confidence_threshold=0.5):
        """
        Use AI to detect sewage lines in an image
        
        Args:
            image_path: Path to the satellite image
            confidence_threshold: How confident the AI must be (0.0-1.0)
                                 Higher = fewer but more certain detections
        
        Returns:
            Binary mask showing detected sewage lines (white = sewage, black = background)
        """
        try:
            # Prepare image for AI
            processed_image = self.preprocess_image(image_path)
            
            # Run AI prediction
            logger.info("Running AI analysis...")
            prediction = self.model.predict(processed_image, verbose=0)
            
            # Convert AI confidence to binary mask
            mask = (prediction[0, :, :, 0] > confidence_threshold).astype(np.uint8) * 255
            
            logger.info("AI analysis completed successfully")
            return mask
        except Exception as e:
            logger.error(f"Error during AI prediction: {str(e)}")
            raise
    
    def create_training_data(self, num_samples=50):
        """
        Create synthetic training data for the AI model
        
        Since real labeled sewage data is hard to get, we create artificial
        satellite-like images with known sewage line patterns.
        
        Args:
            num_samples: Number of training images to create
            
        Returns:
            Tuple of (images, masks) for training
        """
        logger.info(f"Creating {num_samples} synthetic training images...")
        
        images = []
        masks = []
        
        for i in range(num_samples):
            # Create fake satellite image (random ground texture)
            img = np.random.randint(50, 200, (128, 128, 3), dtype=np.uint8)
            
            # Add realistic noise (like real satellite images)
            noise = np.random.normal(0, 15, (128, 128, 3))
            img = np.clip(img + noise, 0, 255).astype(np.uint8)
            
            # Create sewage line pattern
            mask = np.zeros((128, 128), dtype=np.uint8)
            
            # Add random sewage lines
            num_lines = np.random.randint(2, 5)
            for _ in range(num_lines):
                if np.random.random() > 0.5:  # Horizontal pipe
                    y = np.random.randint(10, 118)
                    x_start = np.random.randint(0, 30)
                    x_end = np.random.randint(98, 128)
                    thickness = np.random.randint(2, 4)
                    cv2.line(mask, (x_start, y), (x_end, y), 255, thickness)
                else:  # Vertical pipe
                    x = np.random.randint(10, 118)
                    y_start = np.random.randint(0, 30)
                    y_end = np.random.randint(98, 128)
                    thickness = np.random.randint(2, 4)
                    cv2.line(mask, (x, y_start), (x, y_end), 255, thickness)
            
            # Normalize for training
            img_normalized = img.astype(np.float32) / 255.0
            mask_normalized = mask.astype(np.float32) / 255.0
            
            images.append(img_normalized)
            masks.append(mask_normalized)
        
        return np.array(images), np.array(masks)
    
    def train(self, epochs=8, batch_size=4):
        """
        Train the AI model to detect sewage lines
        
        This teaches the neural network to recognize sewage patterns
        by showing it many examples of images and their correct answers.
        
        Args:
            epochs: How many times to go through all training data
            batch_size: How many images to process at once (smaller = less memory)
        
        Returns:
            Training history (loss, accuracy over time)
        """
        logger.info("Starting AI training process...")
        
        # Create training data
        X_train, y_train = self.create_training_data(50)  # Training set
        X_val, y_val = self.create_training_data(10)      # Validation set
        
        # Prepare data format for training
        y_train = np.expand_dims(y_train, axis=-1)
        y_val = np.expand_dims(y_val, axis=-1)
        
        # Compile model if needed
        if self.model is None:
            self.compile_model()
        
        # Training callbacks for better results
        callbacks = [
            keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=2, min_lr=1e-6)
        ]
        
        # Train the AI model
        logger.info(f"Training AI with {epochs} epochs and batch size {batch_size}")
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("AI training completed successfully!")
        return history

# Create the global model instance
sewage_model = UNetSewageSegmentation()
