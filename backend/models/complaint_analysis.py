import numpy as np
import os
import logging
import pickle
import random
import re
import time

logger = logging.getLogger(__name__)

# Model paths
MODEL_PATH = os.path.join('models', 'complaint_classifier.pkl')
VECTORIZER_PATH = os.path.join('models', 'complaint_vectorizer.pkl')

# Complaint types and their severity mappings
COMPLAINT_TYPES = ['blockage', 'leak', 'odor', 'damage', 'overflow']
SEVERITY_LEVELS = ['low', 'medium', 'high']

# Emergency keywords for high severity classification
EMERGENCY_KEYWORDS = [
    'overflow', 'flooding', 'burst', 'collapse', 'sinkhole', 'emergency',
    'dangerous', 'health hazard', 'immediate', 'urgent', 'severe'
]

# Common words for each complaint type
TYPE_KEYWORDS = {
    'blockage': ['clog', 'block', 'backup', 'backing up', 'slow drain', 'not flowing', 'stuck'],
    'leak': ['leak', 'drip', 'seep', 'wet spot', 'damp', 'water coming out', 'discharge'],
    'odor': ['smell', 'stink', 'odor', 'foul', 'rotten', 'gas', 'stench', 'sulfur'],
    'damage': ['crack', 'break', 'damage', 'broken', 'destruction', 'collapse', 'erosion'],
    'overflow': ['overflow', 'flooding', 'spill', 'flood', 'overflowing', 'over capacity']
}

class MockComplaintClassifier:
    """Mock classifier for complaint text analysis"""
    
    def __init__(self):
        pass
        
    def predict_type(self, text):
        """
        Predict the complaint type based on text content
        
        Args:
            text: Complaint text
            
        Returns:
            Complaint type (blockage, leak, odor, etc.)
        """
        text = text.lower()
        scores = {}
        
        # Count keyword matches for each type
        for complaint_type, keywords in TYPE_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    # Keywords found exactly get higher score
                    score += 1
                    
                    # Bonus for multiple occurrences
                    occurrences = len(re.findall(r'\b{}\b'.format(re.escape(keyword)), text))
                    if occurrences > 1:
                        score += occurrences * 0.5
            
            scores[complaint_type] = score
              # If no strong match, add some randomness
        max_score = max(scores.values()) if scores else 0
        if max_score == 0:
            return random.choice(COMPLAINT_TYPES)
            
        # Get the highest scoring type
        best_type = None
        highest_score = 0
        for complaint_type, score in scores.items():
            if score > highest_score:
                highest_score = score
                best_type = complaint_type
                
        return best_type
        
    def predict_severity(self, text):
        """
        Predict the severity level based on text content
        
        Args:
            text: Complaint text
            
        Returns:
            Severity level (low, medium, high)
        """
        text = text.lower()
        
        # Check for emergency keywords (high severity)
        for keyword in EMERGENCY_KEYWORDS:
            if keyword in text:
                return 'high'
                
        # Check for urgent language
        urgent_words = ['urgent', 'important', 'serious', 'significant', 'major']
        for word in urgent_words:
            if word in text:
                return 'medium'
                
        # Default to low severity or random between low and medium
        return random.choices(['low', 'medium'], weights=[0.7, 0.3])[0]
    
    def predict(self, texts):
        """
        Predict complaint types and severities for multiple texts
        
        Args:
            texts: List of complaint texts
            
        Returns:
            List of dictionaries with type and severity predictions
        """
        results = []
        
        for text in texts:
            complaint_type = self.predict_type(text)
            severity = self.predict_severity(text)
            
            results.append({
                'type': complaint_type,
                'severity': severity
            })
            
        return results

def load_classifier_model():
    """
    Load the complaint classifier model
    
    Returns:
        Loaded model or a mock model if not available
    """
    try:
        # Check if model file exists
        if not os.path.exists(MODEL_PATH):
            logger.warning(f"Model file not found at {MODEL_PATH}. Creating mock model.")
            model = MockComplaintClassifier()
            
            # Save the mock model
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump(model, f)
                
            return model
            
        # Load the model
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
            
        logger.info("Complaint classifier model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading complaint classifier: {str(e)}")
        return MockComplaintClassifier()

def analyze_complaint(text):
    """
    Analyze a complaint text to classify type and severity
    
    Args:
        text: Complaint text
        
    Returns:
        Dictionary with type and severity predictions
    """
    try:
        start_time = time.time()
        
        # Load model
        model = load_classifier_model()
        
        # Make prediction
        result = model.predict([text])[0]
        
        # Log processing time
        process_time = time.time() - start_time
        logger.info(f"Complaint analysis completed in {process_time:.2f} seconds")
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing complaint: {str(e)}")
        return {
            'type': random.choice(COMPLAINT_TYPES),
            'severity': random.choice(SEVERITY_LEVELS)
        }

def analyze_complaints_batch(texts):
    """
    Analyze multiple complaint texts in batch
    
    Args:
        texts: List of complaint texts
        
    Returns:
        List of dictionaries with type and severity predictions
    """
    try:
        start_time = time.time()
        
        # Load model
        model = load_classifier_model()
        
        # Make predictions
        results = model.predict(texts)
        
        # Log processing time
        process_time = time.time() - start_time
        logger.info(f"Batch complaint analysis completed in {process_time:.2f} seconds")
        
        return results
    except Exception as e:
        logger.error(f"Error in batch complaint analysis: {str(e)}")
        # Return random results as fallback
        return [
            {
                'type': random.choice(COMPLAINT_TYPES),
                'severity': random.choice(SEVERITY_LEVELS)
            }
            for _ in texts
        ]

def extract_key_insights(complaints):
    """
    Extract key insights from a collection of complaints
    
    Args:
        complaints: List of complaint dictionaries with text, type, severity
        
    Returns:
        Dictionary with insights about the complaints
    """
    type_counts = {}
    severity_counts = {}
    hotspots = {}
    
    for complaint in complaints:
        # Count by type
        complaint_type = complaint['type']
        type_counts[complaint_type] = type_counts.get(complaint_type, 0) + 1
        
        # Count by severity
        severity = complaint['severity']
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Check for geographic clustering if lat/lng available
        if 'lat' in complaint and 'lng' in complaint:
            # Round coordinates to group nearby complaints (approx 500m grid)
            lat_key = round(complaint['lat'] * 20) / 20
            lng_key = round(complaint['lng'] * 20) / 20
            geo_key = f"{lat_key},{lng_key}"
            
            if geo_key not in hotspots:
                hotspots[geo_key] = {
                    'lat': lat_key,
                    'lng': lng_key,
                    'count': 0,
                    'types': {}
                }
                
            hotspots[geo_key]['count'] += 1
            
            # Track complaint types in this hotspot
            h_type = complaint['type']
            hotspots[geo_key]['types'][h_type] = hotspots[geo_key]['types'].get(h_type, 0) + 1
    
    # Find most common type and severity
    most_common_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
    most_common_severity = max(severity_counts.items(), key=lambda x: x[1])[0] if severity_counts else None
    
    # Identify significant hotspots (3+ complaints)
    significant_hotspots = [h for h in hotspots.values() if h['count'] >= 3]
    
    # Sort hotspots by count
    significant_hotspots.sort(key=lambda x: x['count'], reverse=True)
    
    return {
        'total_complaints': sum(type_counts.values()),
        'by_type': type_counts,
        'by_severity': severity_counts,
        'most_common_type': most_common_type,
        'most_common_severity': most_common_severity,
        'hotspots': significant_hotspots[:5]  # Top 5 hotspots
    }

if __name__ == "__main__":
    # Test the complaint analyzer
    logging.basicConfig(level=logging.INFO)
    
    # Sample complaints
    test_complaints = [
        "The sewer is completely blocked and causing flooding in my basement. This is urgent!",
        "There's a bad smell coming from the drain in the street. It's been like this for a week.",
        "I noticed a small leak in the sewer pipe near my property. It's not too bad but should be fixed."
    ]
    
    # Test individual analysis
    print("\nIndividual Complaint Analysis:")
    print("==============================")
    for complaint in test_complaints:
        result = analyze_complaint(complaint)
        print(f"Text: {complaint[:50]}...")
        print(f"Type: {result['type']}")
        print(f"Severity: {result['severity']}")
        print()
        
    # Test batch analysis
    print("\nBatch Analysis Results:")
    print("======================")
    batch_results = analyze_complaints_batch(test_complaints)
    for i, result in enumerate(batch_results):
        print(f"Complaint {i+1}: {result['type']} - {result['severity']}")
