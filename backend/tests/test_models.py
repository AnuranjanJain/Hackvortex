# filepath: e:\HackVortex\SewageMapAI\backend\tests\test_models.py
import os
import sys
import pytest
import numpy as np
import cv2
from io import BytesIO

# Add the parent directory to the path so we can import the models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.segmentation import create_mock_mask, predict_segmentation
from models.demand_prediction import load_demand_model
from models.complaint_analysis import analyze_complaint
from models.spatial_clustering import cluster_geospatial_points

# Create a temporary test image
@pytest.fixture
def test_image_path():
    test_dir = os.path.join('data', 'test')
    os.makedirs(test_dir, exist_ok=True)
    
    test_image_path = os.path.join(test_dir, 'test_image.jpg')
    
    # Create a simple test image if it doesn't exist
    if not os.path.exists(test_image_path):
        img = np.ones((256, 256, 3), dtype=np.uint8) * 255
        # Add a simple pattern
        cv2.rectangle(img, (50, 50), (200, 200), (0, 0, 0), 2)
        cv2.line(img, (50, 50), (200, 200), (0, 0, 0), 2)
        cv2.imwrite(test_image_path, img)
    
    return test_image_path

def test_mock_mask_generation(test_image_path):
    """Test that mock mask generation works"""
    mask_path = create_mock_mask(test_image_path)
    
    # Check that the mask file was created
    assert os.path.exists(mask_path)
    
    # Check that the mask is a valid image
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    assert mask is not None
    assert mask.shape[0] > 0
    assert mask.shape[1] > 0

def test_segmentation_prediction(test_image_path):
    """Test the segmentation prediction function"""
    mask_path = predict_segmentation(test_image_path)
    
    # Check that the prediction function returns a valid path
    assert mask_path is not None
    assert os.path.exists(mask_path)

def test_demand_prediction_model():
    """Test the demand prediction model"""
    model = load_demand_model()
    
    # Check that the model has the expected method
    assert hasattr(model, 'predict')
    
    # Test the model with some sample data
    sample_data = np.array([
        [50000, 10.0, 5.0, 0.2],  # population, area_sqkm, rainfall_mm, industrial_ratio
    ])
    
    predictions = model.predict(sample_data)
    
    # Check that predictions are reasonable (positive values)
    assert len(predictions) == 1
    assert predictions[0] > 0

def test_complaint_analysis():
    """Test the complaint analysis function"""
    # Test with a clear blockage complaint
    blockage_result = analyze_complaint("The sewer is completely blocked and causing overflow")
    
    # Test with a clear odor complaint
    odor_result = analyze_complaint("There's a terrible smell coming from the drain")
    
    # Check that the function returns dictionaries with expected keys
    assert 'type' in blockage_result
    assert 'severity' in blockage_result
    assert 'type' in odor_result
    assert 'severity' in odor_result
    
    # Blockage complaint should likely be classified as blockage
    assert blockage_result['type'] == 'blockage'
    
    # Odor complaint should likely be classified as odor
    assert odor_result['type'] == 'odor'

def test_spatial_clustering():
    """Test the spatial clustering function"""
    # Create sample points
    sample_points = [
        {'lat': 40.7128, 'lng': -74.0060, 'type': 'blockage'},
        {'lat': 40.7129, 'lng': -74.0061, 'type': 'blockage'},  # Close to first point
        {'lat': 40.7200, 'lng': -74.0200, 'type': 'odor'},      # Far from others
    ]
    
    # Run clustering with small epsilon to create at least 2 clusters
    result = cluster_geospatial_points(sample_points, eps=0.01, min_samples=1)
    
    # Check that the function returns a dictionary with expected keys
    assert 'n_clusters' in result
    assert 'clusters' in result
    assert 'noise_points' in result
    
    # We should have at least 2 clusters
    assert result['n_clusters'] >= 2
    
    # Check that the clusters contain points
    assert len(result['clusters']) > 0
