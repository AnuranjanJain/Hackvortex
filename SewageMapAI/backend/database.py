# filepath: e:\HackVortex\SewageMapAI\backend\database.py
import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# SQLite database file
DATABASE_PATH = 'data/sewagemap.db'

def get_db_connection():
    """
    Create a connection to the SQLite database
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        if conn:
            conn.close()
        raise e

def init_db():
    """
    Initialize the database with required tables if they don't exist
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create tables
        
        # Zones table - contains information about different city zones
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS zones (
            zone_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            district TEXT NOT NULL,
            population INTEGER,
            area_sqkm REAL
        )
        ''')
        
        # Demand data - contains sewage demand and capacity information
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sewage_demand (
            id INTEGER PRIMARY KEY,
            zone_id INTEGER,
            demand_m3 REAL,
            capacity_m3 REAL,
            timestamp TEXT,
            FOREIGN KEY (zone_id) REFERENCES zones (zone_id)
        )
        ''')
        
        # Complaints table - for user-reported issues
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'open',
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        # Illegal connections - detected unauthorized sewage connections
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS illegal_connections (
            id INTEGER PRIMARY KEY,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            confidence REAL NOT NULL,
            type TEXT,
            detected_date TEXT,
            status TEXT DEFAULT 'unverified'
        )
        ''')
        
        # Processed images - to keep track of uploaded and processed images
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_images (
            id INTEGER PRIMARY KEY,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            mask_filename TEXT,
            upload_date TEXT,
            processing_time REAL,
            status TEXT,
            width INTEGER,
            height INTEGER
        )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise e
    finally:
        if conn:
            conn.close()

def insert_sample_data():
    """
    Insert sample data into the database for testing
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if we already have data
        cursor.execute("SELECT COUNT(*) FROM zones")
        if cursor.fetchone()[0] > 0:
            logger.info("Sample data already exists, skipping insertion")
            return
            
        # Insert sample zones
        zones_data = [
            (1, "Downtown", "Central", 75000, 12.5),
            (2, "Westside", "West", 58000, 18.2),
            (3, "Northside", "North", 45000, 22.8),
            (4, "Eastside", "East", 33000, 15.3),
            (5, "Southside", "South", 62000, 20.1)
        ]
        
        cursor.executemany(
            "INSERT INTO zones (zone_id, name, district, population, area_sqkm) VALUES (?, ?, ?, ?, ?)",
            zones_data
        )
        
        # Insert sample sewage demand data
        current_date = datetime.now().strftime("%Y-%m-%d")
        demand_data = [
            (1, 1, 6200, 5800, current_date),
            (2, 2, 4700, 4600, current_date),
            (3, 3, 3500, 4200, current_date),
            (4, 4, 2800, 3200, current_date),
            (5, 5, 5100, 5000, current_date)
        ]
        
        cursor.executemany(
            "INSERT INTO sewage_demand (id, zone_id, demand_m3, capacity_m3, timestamp) VALUES (?, ?, ?, ?, ?)",
            demand_data
        )
        
        # Insert sample complaints
        complaint_data = [
            (1, 40.7128, -74.0060, "blockage", "high", "Complete blockage causing overflow", "open", current_date, current_date),
            (2, 40.7148, -74.0090, "leak", "medium", "Sewage leaking into street", "in_progress", current_date, current_date),
            (3, 40.7080, -74.0021, "odor", "low", "Strong odor in residential area", "open", current_date, current_date),
            (4, 40.7198, -74.0110, "blockage", "medium", "Partial blockage with slow drainage", "open", current_date, current_date),
            (5, 40.7220, -73.9890, "damage", "high", "Collapsed pipe section causing sinkholes", "in_progress", current_date, current_date)
        ]
        
        cursor.executemany(
            "INSERT INTO complaints (id, lat, lng, type, severity, description, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            complaint_data
        )
        
        # Insert sample illegal connections
        illegal_connections_data = [
            (1, 40.7200, -74.0050, 0.89, "industrial", current_date, "unverified"),
            (2, 40.7180, -74.0070, 0.76, "residential", current_date, "unverified"),
            (3, 40.7130, -74.0020, 0.92, "commercial", current_date, "confirmed"),
            (4, 40.7160, -74.0010, 0.68, "residential", current_date, "unverified"),
            (5, 40.7210, -73.9950, 0.85, "industrial", current_date, "confirmed")
        ]
        
        cursor.executemany(
            "INSERT INTO illegal_connections (id, lat, lng, confidence, type, detected_date, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            illegal_connections_data
        )
        
        conn.commit()
        logger.info("Sample data inserted successfully")
    except sqlite3.Error as e:
        logger.error(f"Error inserting sample data: {str(e)}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Insert sample data
    insert_sample_data()
