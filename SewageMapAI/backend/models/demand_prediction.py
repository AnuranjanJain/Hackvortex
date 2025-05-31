import numpy as np
import os
import logging
import joblib
import random
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Model path
MODEL_PATH = os.path.join('models', 'xgboost_demand_model.joblib')

# Define MockXGBoostModel as a top-level class so it can be properly serialized
class MockXGBoostModel:
    def __init__(self):
        self.feature_importances_ = {
            'population': 0.45,
            'area_sqkm': 0.15,
            'rainfall_mm': 0.25,
            'industrial_ratio': 0.15
        }
        
    def predict(self, X):
        """
        Predict sewage demand based on input features
        
        Args:
            X: Array-like of shape (n_samples, n_features)
               Features should be: population, area_sqkm, rainfall_mm, industrial_ratio
               
        Returns:
            Array of predicted sewage demand in cubic meters
        """
        predictions = []
        
        for sample in X:
            population, area_sqkm, rainfall_mm, industrial_ratio = sample
            
            # Base demand calculation (simplified model)
            base_demand = population * 0.15  # 150 liters per person per day
            
            # Adjust for area size (density factor)
            density_factor = 1.0 + (0.2 * (1.0 - (area_sqkm / (population / 1000))))
            
            # Adjust for rainfall (more rain means more inflow to sewage system)
            rainfall_factor = 1.0 + (0.01 * rainfall_mm)
            
            # Adjust for industrial presence (industries use more water)
            industrial_factor = 1.0 + (0.5 * industrial_ratio)
            
            # Calculate final prediction with some randomness
            prediction = base_demand * density_factor * rainfall_factor * industrial_factor
              # Add some noise (5% variance)
            noise_factor = random.uniform(0.95, 1.05)
            prediction *= noise_factor
            predictions.append(round(prediction, 1))
        
        return np.array(predictions)

def create_mock_model():
    """
    Create a mock model for sewage demand prediction
    
    Returns:
        A callable object that predicts sewage demand
    """
    return MockXGBoostModel()

def load_demand_model():
    """
    Load the XGBoost model for sewage demand prediction
    
    Returns:
        Loaded model or a mock model if not available
    """
    try:
        # Check if model file exists
        if not os.path.exists(MODEL_PATH):
            logger.warning(f"Model file not found at {MODEL_PATH}. Creating mock model.")
            model = create_mock_model()
            
            # Save the mock model
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            joblib.dump(model, MODEL_PATH)
            
            return model
        
        # Load the model
        model = joblib.load(MODEL_PATH)
        logger.info("Demand prediction model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading demand prediction model: {str(e)}")
        return create_mock_model()

def predict_future_demand(zone_data, days=30):
    """
    Predict sewage demand for the next specified number of days
    
    Args:
        zone_data: Dictionary with zone information including population, area_sqkm
        days: Number of days to predict into the future
        
    Returns:
        Dictionary with daily predictions
    """
    try:
        start_time = time.time()
        
        # Load prediction model
        model = load_demand_model()
        
        # Generate weather forecast (mocked data)
        today = datetime.now()
        forecast = []
        
        for i in range(days):
            date = today + timedelta(days=i)
            
            # Generate synthetic rainfall data with seasonal pattern
            month = date.month
            if 3 <= month <= 5:  # Spring
                base_rainfall = 5
                variance = 10
            elif 6 <= month <= 8:  # Summer
                base_rainfall = 3
                variance = 15
            elif 9 <= month <= 11:  # Fall
                base_rainfall = 7
                variance = 12
            else:  # Winter
                base_rainfall = 4
                variance = 8
                
            rainfall = max(0, base_rainfall + random.uniform(-variance, variance))
            
            # Add some correlation between consecutive days
            if i > 0:
                prev_rainfall = forecast[i-1]['rainfall_mm']
                rainfall = (rainfall + prev_rainfall) / 2
                
            forecast.append({
                'date': date.strftime('%Y-%m-%d'),
                'rainfall_mm': round(rainfall, 1)
            })
        
        # Prepare predictions for each day
        predictions = []
        base_demand = None
        
        for day in forecast:
            # Prepare features
            industrial_ratio = zone_data.get('industrial_ratio', random.uniform(0.1, 0.4))
            features = np.array([
                [
                    zone_data['population'],
                    zone_data['area_sqkm'],
                    day['rainfall_mm'],
                    industrial_ratio
                ]
            ])
            
            # Predict demand
            demand = float(model.predict(features)[0])
            
            # Set base demand for the first day
            if base_demand is None:
                base_demand = demand
            
            # Add to predictions
            predictions.append({
                'date': day['date'],
                'demand_m3': demand,
                'rainfall_mm': day['rainfall_mm']
            })
        
        # Log processing time
        process_time = time.time() - start_time
        logger.info(f"Demand prediction completed in {process_time:.2f} seconds")
        
        return predictions
    except Exception as e:
        logger.error(f"Error in demand prediction: {str(e)}")
        return []

if __name__ == "__main__":
    # Test the model
    logging.basicConfig(level=logging.INFO)
    
    # Sample zone data
    zone = {
        'zone_id': 1,
        'name': 'Downtown',
        'district': 'Central',
        'population': 75000,
        'area_sqkm': 12.5
    }
    
    # Make prediction
    predictions = predict_future_demand(zone, days=7)
    
    # Print results
    print("\nDemand Predictions for Next 7 Days:")
    print("===================================")
    for pred in predictions:
        print(f"Date: {pred['date']}, Rainfall: {pred['rainfall_mm']}mm, Demand: {pred['demand_m3']:.1f} m³")
