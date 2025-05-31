from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
import logging
import uuid
from PIL import Image
import traceback

# Import models
from models.segmentation import predict_segmentation

logger = logging.getLogger(__name__)
image_bp = Blueprint('image_bp', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'tif', 'tiff'}

@image_bp.route('/upload-image', methods=['POST'])
def upload_image():
    """
    Upload a satellite image and run segmentation to detect sewage lines
    """
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    # Check if the file is empty
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
      # Check if the file is allowed
    if file and file.filename and allowed_file(file.filename):
        try:
            # Generate unique filename to prevent overwriting
            original_filename = secure_filename(file.filename)
            filename_parts = original_filename.rsplit('.', 1)
            unique_filename = f"{filename_parts[0]}_{uuid.uuid4().hex[:8]}.{filename_parts[1]}"
            
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Basic image validation
            try:
                with Image.open(file_path) as img:
                    # Check if image dimensions are reasonable
                    width, height = img.size
                    if width < 100 or height < 100:
                        os.remove(file_path)
                        return jsonify({"error": "Image dimensions too small. Min size: 100x100px"}), 400
                    if width > 10000 or height > 10000:
                        os.remove(file_path)
                        return jsonify({"error": "Image dimensions too large. Max size: 10000x10000px"}), 400
            except Exception as e:
                os.remove(file_path)
                logger.error(f"Invalid image file: {str(e)}")
                return jsonify({"error": "Invalid image file"}), 400            # Process the image with the real AI segmentation model
            logger.info("Processing image with AI model...")
            
            # Use the real AI model for segmentation
            mask_file_path, detection_results = predict_segmentation(file_path)
            
            if mask_file_path is None:
                return jsonify({"error": "Failed to process image with AI model"}), 500
            
            # Get the relative path for the frontend
            mask_filename = os.path.basename(mask_file_path)
            mask_path = f"/uploads/{mask_filename}"
            
            return jsonify({
                "success": True,
                "original_image": f"/uploads/{unique_filename}",
                "segmentation_mask": mask_path,
                "message": "Image uploaded and processed successfully",
                "dimensions": {
                    "width": width,
                    "height": height
                },
                "detection_results": detection_results
            })
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({"error": f"Error processing image: {str(e)}"}), 500
    
    return jsonify({"error": "File type not allowed. Supported formats: PNG, JPG, JPEG, TIF, TIFF"}), 400

@image_bp.route('/image-stats', methods=['GET'])
def get_image_stats():
    """
    Get statistics about processed images
    """
    try:
        # In a production environment, this would pull data from a database
        # For now, return mock statistics
        return jsonify({
            "total_processed": 127,
            "success_rate": 94.5,
            "avg_processing_time": 2.3,
            "last_processed": "2025-04-23T14:52:09Z"
        })
    except Exception as e:
        logger.error(f"Error retrieving image stats: {str(e)}")
        return jsonify({"error": str(e)}), 500
