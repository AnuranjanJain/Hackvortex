from flask import Blueprint, jsonify, request
import pandas as pd
import os
import logging
import traceback

from database import get_db_connection

logger = logging.getLogger(__name__)
data_bp = Blueprint('data_bp', __name__)

# Path to data files
DATA_PATH = 'data'

@data_bp.route('/sewage-demand', methods=['GET'])
def get_sewage_demand():
    """
    Return sewage demand data from the database
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Join with zones to get district names
        query = """
        SELECT sd.id, sd.zone_id, z.district, z.population, sd.demand_m3, sd.capacity_m3, sd.timestamp
        FROM sewage_demand sd
        JOIN zones z ON sd.zone_id = z.zone_id
        ORDER BY sd.id
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        sewage_data = []
        for row in results:
            sewage_data.append({
                "id": row["id"],
                "zone_id": row["zone_id"],
                "district": row["district"],
                "population": row["population"],
                "demand_m3": row["demand_m3"],
                "capacity_m3": row["capacity_m3"],
                "timestamp": row["timestamp"]
            })
        
        conn.close()
        
        return jsonify({
            "data": sewage_data,
            "count": len(sewage_data)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving sewage demand data: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Fallback to mock data if database access fails
        mock_data = [
            {"zone_id": 1, "district": "North", "population": 45000, "demand_m3": 3500, "capacity_m3": 4200},
            {"zone_id": 2, "district": "South", "population": 62000, "demand_m3": 5100, "capacity_m3": 5000},
            {"zone_id": 3, "district": "East", "population": 33000, "demand_m3": 2800, "capacity_m3": 3200},
            {"zone_id": 4, "district": "West", "population": 58000, "demand_m3": 4700, "capacity_m3": 4600},
            {"zone_id": 5, "district": "Central", "population": 75000, "demand_m3": 6200, "capacity_m3": 5800}
        ]
        
        return jsonify({
            "data": mock_data,
            "count": len(mock_data),
            "warning": "Using mock data due to database error"
        })

@data_bp.route('/complaints', methods=['GET'])
def get_complaints():
    """
    Return geotagged complaints data from the database
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Optional filtering by severity
        severity_filter = request.args.get('severity')
        
        if severity_filter:
            query = "SELECT * FROM complaints WHERE severity = ? ORDER BY created_at DESC"
            cursor.execute(query, (severity_filter,))
        else:
            query = "SELECT * FROM complaints ORDER BY created_at DESC"
            cursor.execute(query)
            
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        complaints_data = []
        for row in results:
            complaints_data.append({
                "id": row["id"],
                "lat": row["lat"],
                "lng": row["lng"],
                "type": row["type"],
                "severity": row["severity"],
                "description": row["description"],
                "status": row["status"],
                "created_at": row["created_at"]
            })
        
        conn.close()
        
        return jsonify({
            "data": complaints_data,
            "count": len(complaints_data)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving complaints data: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Fallback to mock data if database access fails
        mock_data = [
            {"id": 1, "lat": 40.7128, "lng": -74.0060, "type": "blockage", "severity": "high", "description": "Complete blockage causing overflow"},
            {"id": 2, "lat": 40.7148, "lng": -74.0090, "type": "leak", "severity": "medium", "description": "Sewage leaking into street"},
            {"id": 3, "lat": 40.7080, "lng": -74.0021, "type": "odor", "severity": "low", "description": "Strong odor in residential area"},
            {"id": 4, "lat": 40.7198, "lng": -74.0110, "type": "blockage", "severity": "medium", "description": "Partial blockage with slow drainage"},
            {"id": 5, "lat": 40.7220, "lng": -73.9890, "type": "damage", "severity": "high", "description": "Collapsed pipe section causing sinkholes"}
        ]
        
        return jsonify({
            "data": mock_data,
            "count": len(mock_data),
            "warning": "Using mock data due to database error"
        })

@data_bp.route('/illegal-connections', methods=['GET'])
def get_illegal_connections():
    """
    Return data about suspected illegal sewage connections from the database
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Optional filtering by confidence threshold
        confidence_threshold = request.args.get('confidence_threshold', 0.0, type=float)
        status_filter = request.args.get('status')
        
        query_parts = ["SELECT * FROM illegal_connections"]
        query_conditions = []
        query_params = []
        
        if confidence_threshold > 0:
            query_conditions.append("confidence >= ?")
            query_params.append(confidence_threshold)
            
        if status_filter:
            query_conditions.append("status = ?")
            query_params.append(status_filter)
        
        if query_conditions:
            query_parts.append("WHERE " + " AND ".join(query_conditions))
            
        query_parts.append("ORDER BY confidence DESC")
        
        query = " ".join(query_parts)
        cursor.execute(query, query_params)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        illegal_connections_data = []
        for row in results:
            illegal_connections_data.append({
                "id": row["id"],
                "lat": row["lat"],
                "lng": row["lng"],
                "confidence": row["confidence"],
                "type": row["type"],
                "detected_date": row["detected_date"],
                "status": row["status"]
            })
        
        conn.close()
        
        return jsonify({
            "data": illegal_connections_data, 
            "count": len(illegal_connections_data)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving illegal connections data: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Fallback to mock data if database access fails
        mock_data = [
            {"id": 1, "lat": 40.7200, "lng": -74.0050, "confidence": 0.89, "detected_date": "2025-04-12", "type": "industrial"},
            {"id": 2, "lat": 40.7180, "lng": -74.0070, "confidence": 0.76, "detected_date": "2025-04-18", "type": "residential"},
            {"id": 3, "lat": 40.7130, "lng": -74.0020, "confidence": 0.92, "detected_date": "2025-04-05", "type": "commercial"},
            {"id": 4, "lat": 40.7160, "lng": -74.0010, "confidence": 0.68, "detected_date": "2025-04-22", "type": "residential"},
            {"id": 5, "lat": 40.7210, "lng": -73.9950, "confidence": 0.85, "detected_date": "2025-04-15", "type": "industrial"}        ]
        
        return jsonify({
            "data": mock_data, 
            "count": len(mock_data),
            "warning": "Using mock data due to database error"
        })

@data_bp.route('/demand/predict', methods=['POST'])
def predict_demand():
    """
    Predict sewage demand for a specified zone
    """
    try:
        # Get request data
        data = request.get_json()
        zone_id = data.get('zone_id')
        days = data.get('days', 30)  # Default to 30 days if not provided
        
        if not zone_id:
            return jsonify({"error": "Zone ID is required"}), 400
            
        # Get zone information from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM zones WHERE zone_id = ?"
        cursor.execute(query, (zone_id,))
        zone = cursor.fetchone()
        
        conn.close()
        
        if not zone:
            return jsonify({"error": f"Zone with ID {zone_id} not found"}), 404
            
        # Import here to avoid circular imports
        from models.demand_prediction import predict_future_demand
        
        # Generate demand prediction
        predictions = predict_future_demand(zone, days=days)
        
        return jsonify({
            "zone_id": zone_id,
            "zone_name": zone["name"],
            "district": zone["district"],
            "predictions": predictions,
            "days": days
        })
        
    except Exception as e:
        logger.error(f"Error in demand prediction: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to process demand prediction"}), 500
