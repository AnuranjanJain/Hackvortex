# filepath: e:\HackVortex\SewageMapAI\backend\setup.py
import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        logger.error(f"{requirements_file} not found.")
        return False
    
    try:
        import pkg_resources
        
        # Read requirements file
        with open(requirements_file, "r") as f:
            requirements = f.readlines()
        
        # Clean up requirements and filter out comments
        requirements = [r.strip() for r in requirements if r.strip() and not r.strip().startswith("#")]
        
        # Check each requirement
        missing = []
        for requirement in requirements:
            try:
                pkg_resources.require(requirement) # type: ignore
            except Exception:
                missing.append(requirement)
        
        if missing:
            logger.warning(f"Missing dependencies: {', '.join(missing)}")
            return False
            
        logger.info("All dependencies are installed.")
        return True
        
    except ImportError:
        logger.warning("Could not check dependencies. pkg_resources not available.")
        return False

def install_dependencies():
    """Install dependencies from requirements.txt"""
    logger.info("Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing dependencies: {e}")
        return False

def setup_database():
    """Set up the database and initialize it with sample data"""
    logger.info("Setting up database...")
    
    try:
        from database import init_db, insert_sample_data
        
        init_db()
        insert_sample_data()
        
        logger.info("Database setup complete.")
        return True
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        return False

def create_folders():
    """Create necessary folders for the application"""
    folders = [
        "data",
        "data/uploads",
        "data/outputs",
        "models"
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        logger.info(f"Created folder: {folder}")

def preload_models():
    """Preload AI models to ensure they're ready"""
    logger.info("Loading AI models...")
    
    try:
        # Attempt to load each model
        from models.segmentation import predict_segmentation
        from models.demand_prediction import load_demand_model
        from models.complaint_analysis import load_classifier_model
        from models.spatial_clustering import load_clustering_model
        
        # Create a test image for segmentation
        test_dir = os.path.join('data', 'test')
        os.makedirs(test_dir, exist_ok=True)
        test_image = os.path.join(test_dir, 'test.jpg')
        
        import numpy as np
        import cv2
        
        # Create a simple test image
        img = np.ones((256, 256, 3), dtype=np.uint8) * 255
        cv2.rectangle(img, (50, 50), (200, 200), (0, 0, 0), 2)
        cv2.imwrite(test_image, img)
        
        # Run each model once
        logger.info("Loading segmentation model...")
        predict_segmentation(test_image)
        
        logger.info("Loading demand prediction model...")
        load_demand_model()
        
        logger.info("Loading complaint analysis model...")
        load_classifier_model()
        
        logger.info("Loading spatial clustering model...")
        load_clustering_model()
        
        logger.info("All models loaded successfully.")
        return True
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        return False

def main():
    """Main setup function"""
    print("\n" + "=" * 50)
    print("SewageMapAI Backend Setup")
    print("=" * 50 + "\n")
    
    # Create required folders
    create_folders()
    
    # Check and install dependencies
    if not check_dependencies():
        print("\nInstalling missing dependencies...")
        install_dependencies()
    
    # Set up database
    print("\nSetting up database...")
    setup_database()
    
    # Preload models
    print("\nPreloading AI models...")
    preload_models()
    
    print("\n" + "=" * 50)
    print("Setup complete! You can now start the server with:")
    print("python app.py")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
