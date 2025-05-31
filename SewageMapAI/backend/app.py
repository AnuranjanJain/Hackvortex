from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
import numpy as np
import logging
from werkzeug.utils import secure_filename
from functools import wraps
import json

# Setup logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.FileHandler("app.log"),
                             logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='data')
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'uploads'))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff'}
MODEL_FOLDER = 'models'
DATA_FOLDER = 'data'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Validation decorator
def validate_json_data(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if request has JSON data
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400
            
            data = request.get_json()
            
            # Validate required fields
            for field in schema:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
                
                # Type validation if specified in schema
                if isinstance(schema[field], dict) and 'type' in schema[field]:
                    if schema[field]['type'] == 'number' and not isinstance(data[field], (int, float)):
                        return jsonify({"error": f"Field {field} must be a number"}), 400
                    elif schema[field]['type'] == 'string' and not isinstance(data[field], str):
                        return jsonify({"error": f"Field {field} must be a string"}), 400
                    elif schema[field]['type'] == 'array' and not isinstance(data[field], list):
                        return jsonify({"error": f"Field {field} must be an array"}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Import routes
from routes.image_routes import image_bp
from routes.data_routes import data_bp

# Register blueprints
app.register_blueprint(image_bp)
app.register_blueprint(data_bp)

@app.route('/')
def index():
    return jsonify({"message": "Welcome to SewageMapAI API!"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files from the uploads directory"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(400)
def bad_request(error):
    logger.error(f"Bad request: {error}")
    return jsonify({"error": "Bad request. Please check your input data"}), 400

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

if __name__ == '__main__':
    # Create necessary folders if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join('data', 'outputs'), exist_ok=True)
    
    # Initialize database
    from database import init_db, insert_sample_data
    init_db()
    insert_sample_data()
    
    # Load models preemptively
    try:
        from models.segmentation import predict_segmentation
        from models.demand_prediction import load_demand_model
        from models.complaint_analysis import load_classifier_model
        from models.spatial_clustering import load_clustering_model
        
        # Preload models in background
        logger.info("Preloading AI models...")
        load_demand_model()
        load_classifier_model()
        load_clustering_model()
        
        logger.info("All models loaded successfully")
    except Exception as e:
        logger.error(f"Error preloading models: {str(e)}")
    
    app.run(debug=True)
