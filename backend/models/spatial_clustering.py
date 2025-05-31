import numpy as np
import os
import logging
import pickle
import time
import random
from math import radians, sin, cos, sqrt, atan2

logger = logging.getLogger(__name__)

# Model path
MODEL_PATH = os.path.join('models', 'spatial_clustering_model.pkl')

# Distance calculation function (Haversine formula)
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    
    Args:
        lat1, lon1: Coordinates of point 1
        lat2, lon2: Coordinates of point 2
        
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = 6371 * c  # Earth radius in kilometers
    
    return distance

class MockDBSCANClustering:
    """
    Mock implementation of DBSCAN clustering algorithm for spatial data
    """
    def __init__(self, eps=0.5, min_samples=5):
        """
        Initialize the clustering model
        
        Args:
            eps: Maximum distance between two points to be considered neighbors (km)
            min_samples: Minimum number of points to form a cluster
        """
        self.eps = eps
        self.min_samples = min_samples
        
    def fit_predict(self, X):
        """
        Fit the model and predict cluster labels
        
        Args:
            X: Array of shape (n_samples, 2) with lat, lng coordinates
            
        Returns:
            Array of cluster labels (-1 for noise points)
        """
        if len(X) == 0:
            return np.array([])
            
        n_samples = len(X)
        # Initialize all points as unvisited
        visited = np.zeros(n_samples, dtype=bool)
        # Initialize all points as noise
        labels = np.full(n_samples, -1)
        
        cluster_id = 0
        
        # Process each point
        for i in range(n_samples):
            # Skip if already visited
            if visited[i]:
                continue
                
            visited[i] = True
            
            # Find neighbors
            neighbors = []
            for j in range(n_samples):
                if i == j:
                    continue
                    
                # Calculate distance between points
                distance = haversine_distance(X[i][0], X[i][1], X[j][0], X[j][1])
                
                if distance <= self.eps:
                    neighbors.append(j)
            
            # Check if this point has enough neighbors to form a cluster
            if len(neighbors) < self.min_samples - 1:  # -1 because the point itself counts
                # Mark as noise for now
                continue
                
            # Start a new cluster
            labels[i] = cluster_id
            
            # Process all neighbors
            j = 0
            while j < len(neighbors):
                neighbor = neighbors[j]
                
                # If not visited, mark as visited
                if not visited[neighbor]:
                    visited[neighbor] = True
                    
                    # Find neighbors of this neighbor
                    new_neighbors = []
                    for k in range(n_samples):
                        if neighbor == k:
                            continue
                            
                        distance = haversine_distance(X[neighbor][0], X[neighbor][1], X[k][0], X[k][1])
                        
                        if distance <= self.eps:
                            new_neighbors.append(k)
                    
                    # If enough neighbors, add them to the list for processing
                    if len(new_neighbors) >= self.min_samples - 1:
                        neighbors.extend(new_neighbors)
                
                # If not already in a cluster, add to current cluster
                if labels[neighbor] == -1:
                    labels[neighbor] = cluster_id
                    
                j += 1
                
            # Move to next cluster
            cluster_id += 1
            
        return labels

def load_clustering_model(eps=0.5, min_samples=5):
    """
    Load the spatial clustering model
    
    Args:
        eps: Maximum distance between two points to be considered neighbors (km)
        min_samples: Minimum number of points to form a cluster
        
    Returns:
        Loaded model or a new one if not available
    """
    try:
        # Check if model file exists
        if not os.path.exists(MODEL_PATH):
            logger.warning(f"Model file not found at {MODEL_PATH}. Creating new model.")
            model = MockDBSCANClustering(eps=eps, min_samples=min_samples)
            
            # Save the model
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump(model, f)
                
            return model
                
        # Load the model
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
            
        # Update parameters
        model.eps = eps
        model.min_samples = min_samples
            
        logger.info("Spatial clustering model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading spatial clustering model: {str(e)}")
        return MockDBSCANClustering(eps=eps, min_samples=min_samples)

def cluster_geospatial_points(points, eps=0.5, min_samples=5):
    """
    Cluster geospatial points using DBSCAN
    
    Args:
        points: List of dictionaries with lat, lng keys
        eps: Maximum distance between points to be neighbors (km)
        min_samples: Minimum points to form a cluster
        
    Returns:
        Dictionary with cluster information
    """
    try:
        start_time = time.time()
        
        # Extract coordinates
        coords = np.array([[p['lat'], p['lng']] for p in points])
        
        # Load model
        model = load_clustering_model(eps=eps, min_samples=min_samples)
        
        # Perform clustering
        labels = model.fit_predict(coords)
        
        # Count number of clusters (-1 is noise)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        # Group points by cluster
        clusters = {}
        for i, label in enumerate(labels):
            if label == -1:
                # Skip noise points
                continue
                
            if label not in clusters:
                clusters[label] = []
                
            clusters[label].append(points[i])
            
        # Calculate statistics for each cluster
        cluster_stats = []
        for label, cluster_points in clusters.items():
            # Calculate centroid
            lats = [p['lat'] for p in cluster_points]
            lngs = [p['lng'] for p in cluster_points]
            
            centroid = {
                'lat': sum(lats) / len(lats),
                'lng': sum(lngs) / len(lngs)
            }
            
            # Find dominant characteristics
            types = {}
            severities = {}
            
            for p in cluster_points:
                if 'type' in p:
                    types[p['type']] = types.get(p['type'], 0) + 1
                if 'severity' in p:
                    severities[p['severity']] = severities.get(p['severity'], 0) + 1
            
            dominant_type = max(types.items(), key=lambda x: x[1])[0] if types else None
            dominant_severity = max(severities.items(), key=lambda x: x[1])[0] if severities else None
            
            # Add stats to result
            cluster_stats.append({
                'cluster_id': int(label),
                'size': len(cluster_points),
                'centroid': centroid,
                'dominant_type': dominant_type,
                'dominant_severity': dominant_severity,
                'points': cluster_points
            })
            
        # Sort clusters by size
        cluster_stats.sort(key=lambda x: x['size'], reverse=True)
        
        # Calculate noise points
        noise_points = [points[i] for i, label in enumerate(labels) if label == -1]
        
        # Log processing time
        process_time = time.time() - start_time
        logger.info(f"Spatial clustering completed in {process_time:.2f} seconds")
        
        return {
            'n_clusters': n_clusters,
            'clusters': cluster_stats,
            'noise_points': noise_points,
            'noise_ratio': len(noise_points) / len(points) if points else 0
        }
    except Exception as e:
        logger.error(f"Error in spatial clustering: {str(e)}")
        return {
            'n_clusters': 0,
            'clusters': [],
            'noise_points': points,
            'noise_ratio': 1.0,
            'error': str(e)
        }

def detect_illegal_connections(complaint_points, rainfall_events, sewage_network=None):
    """
    Use spatial clustering and temporal correlation to detect potential illegal connections
    
    Args:
        complaint_points: List of complaint points with coordinates and timestamps
        rainfall_events: List of rainfall events with coordinates, intensity, and timestamps
        sewage_network: Optional sewage network data
        
    Returns:
        List of potential illegal connection points
    """
    try:
        # In a real implementation, this would analyze the correlation between
        # rainfall events and sewage overflow complaints to detect illegal connections
        # For now, we'll generate some mock detections
        
        # Mock implementation: Generate some detections based on complaint clusters
        model = load_clustering_model(eps=0.3, min_samples=3)
        
        # Extract coordinates from complaints
        if not complaint_points:
            return []
            
        coords = np.array([[p['lat'], p['lng']] for p in complaint_points])
        
        # Perform clustering
        labels = model.fit_predict(coords)
        
        # Find cluster centroids
        clusters = {}
        for i, label in enumerate(labels):
            if label == -1:
                continue
                
            if label not in clusters:
                clusters[label] = []
                
            clusters[label].append(complaint_points[i])
        
        # Create illegal connection detections near cluster edges
        illegal_connections = []
        
        for label, points in clusters.items():
            # For each cluster, generate 1-3 potential illegal connections
            n_detections = random.randint(1, 3)
            
            for _ in range(n_detections):
                # Calculate centroid
                lats = [p['lat'] for p in points]
                lngs = [p['lng'] for p in points]
                
                center_lat = sum(lats) / len(lats)
                center_lng = sum(lngs) / len(lngs)
                
                # Add some random offset (100-500m)
                offset_lat = random.uniform(-0.001, 0.001)
                offset_lng = random.uniform(-0.001, 0.001)
                
                # Create a detection with random confidence and type
                detection = {
                    'lat': center_lat + offset_lat,
                    'lng': center_lng + offset_lng,
                    'confidence': random.uniform(0.6, 0.95),
                    'type': random.choice(['residential', 'industrial', 'commercial']),
                    'detection_method': 'spatial_clustering'
                }
                
                illegal_connections.append(detection)
        
        # Add a few random detections
        n_random = random.randint(1, 5)
        for _ in range(n_random):
            # Find a random base point
            if complaint_points:
                base_point = random.choice(complaint_points)
                base_lat = base_point['lat']
                base_lng = base_point['lng']
            else:
                # Default to New York City if no complaint points
                base_lat = 40.7128
                base_lng = -74.0060
                
            # Add a larger random offset (500m-2km)
            offset_lat = random.uniform(-0.02, 0.02)
            offset_lng = random.uniform(-0.02, 0.02)
            
            # Create a detection
            detection = {
                'lat': base_lat + offset_lat,
                'lng': base_lng + offset_lng,
                'confidence': random.uniform(0.5, 0.85),
                'type': random.choice(['residential', 'industrial', 'commercial']),
                'detection_method': 'anomaly_detection'
            }
            
            illegal_connections.append(detection)
            
        return illegal_connections
    except Exception as e:
        logger.error(f"Error in illegal connection detection: {str(e)}")
        return []

if __name__ == "__main__":
    # Test the clustering model
    logging.basicConfig(level=logging.INFO)
    
    # Sample points (New York City area)
    sample_points = [
        {'lat': 40.7128, 'lng': -74.0060, 'type': 'blockage', 'severity': 'high'},
        {'lat': 40.7129, 'lng': -74.0063, 'type': 'blockage', 'severity': 'medium'},
        {'lat': 40.7131, 'lng': -74.0065, 'type': 'leak', 'severity': 'low'},
        {'lat': 40.7200, 'lng': -74.0100, 'type': 'odor', 'severity': 'medium'},
        {'lat': 40.7198, 'lng': -74.0105, 'type': 'odor', 'severity': 'low'},
        {'lat': 40.7301, 'lng': -74.0020, 'type': 'damage', 'severity': 'high'},
        {'lat': 40.7298, 'lng': -74.0022, 'type': 'damage', 'severity': 'high'},
        {'lat': 40.7500, 'lng': -73.9800, 'type': 'blockage', 'severity': 'medium'},
    ]
    
    # Run clustering
    result = cluster_geospatial_points(sample_points, eps=0.2, min_samples=2)
    
    # Print results
    print(f"\nFound {result['n_clusters']} clusters:")
    for i, cluster in enumerate(result['clusters']):
        print(f"Cluster {i+1}: {cluster['size']} points")
        print(f"  Centroid: {cluster['centroid']['lat']:.4f}, {cluster['centroid']['lng']:.4f}")
        print(f"  Type: {cluster['dominant_type']}, Severity: {cluster['dominant_severity']}")
        print()
        
    # Test illegal connection detection
    print("\nIllegal Connection Detection Test:")
    illegal = detect_illegal_connections(sample_points, [])
    
    for i, connection in enumerate(illegal):
        print(f"Illegal connection {i+1}: {connection['lat']:.4f}, {connection['lng']:.4f}")
        print(f"  Confidence: {connection['confidence']:.2f}, Type: {connection['type']}")
        print(f"  Method: {connection['detection_method']}")
        print()
