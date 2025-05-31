#!/usr/bin/env python3

import sqlite3
import random
import json
from datetime import datetime, timedelta
import logging
import numpy as np
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DATABASE_PATH = 'data/sewagemap.db'

def clear_existing_data():
    """Clear existing sample data"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM processed_images")
        cursor.execute("DELETE FROM illegal_connections")
        cursor.execute("DELETE FROM complaints")
        cursor.execute("DELETE FROM sewage_demand")
        cursor.execute("DELETE FROM zones")
        
        conn.commit()
        logger.info("Existing data cleared")
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
    finally:
        conn.close()

def generate_comprehensive_zones():
    """Generate realistic zone data for a major city"""
    zones_data = [
        # Central districts
        (1, "Manhattan South", "Financial District", 95000, 8.2),
        (2, "Manhattan Midtown", "Midtown", 125000, 12.5),
        (3, "Manhattan Upper West", "Upper West Side", 85000, 15.8),
        (4, "Manhattan Upper East", "Upper East Side", 78000, 14.2),
        (5, "Manhattan Harlem", "Harlem", 92000, 18.5),
        
        # Brooklyn districts  
        (6, "Brooklyn Heights", "Brooklyn North", 67000, 22.3),
        (7, "Park Slope", "Brooklyn Central", 89000, 19.8),
        (8, "Williamsburg", "Brooklyn North", 156000, 16.4),
        (9, "Crown Heights", "Brooklyn Central", 134000, 25.1),
        (10, "Bay Ridge", "Brooklyn South", 78000, 20.7),
        
        # Queens districts
        (11, "Long Island City", "Queens West", 112000, 18.9),
        (12, "Flushing", "Queens East", 198000, 28.4),
        (13, "Astoria", "Queens West", 145000, 22.1),
        (14, "Jamaica", "Queens Central", 167000, 32.6),
        (15, "Forest Hills", "Queens Central", 89000, 24.3),
        
        # Bronx districts
        (16, "South Bronx", "Bronx South", 234000, 35.8),
        (17, "Bronx Park", "Bronx Central", 156000, 28.9),
        (18, "Riverdale", "Bronx North", 67000, 19.4),
        (19, "Fordham", "Bronx Central", 189000, 31.2),
        (20, "Throgs Neck", "Bronx East", 98000, 22.7),
        
        # Staten Island districts
        (21, "St. George", "Staten Island North", 45000, 12.8),
        (22, "New Springville", "Staten Island Central", 78000, 25.3),
        (23, "Tottenville", "Staten Island South", 34000, 18.9),
        (24, "Port Richmond", "Staten Island West", 56000, 21.4),
        (25, "Great Kills", "Staten Island East", 67000, 28.1)
    ]
    
    return zones_data

def generate_demand_data(zones_data):
    """Generate realistic sewage demand data with time series"""
    demand_data = []
    current_date = datetime.now()
    
    for zone_id, name, district, population, area in zones_data:
        # Base demand calculation (population-based with some randomness)
        base_demand = population * random.uniform(0.08, 0.12)  # 80-120 liters per person per day
        base_capacity = base_demand * random.uniform(1.1, 1.4)  # 110-140% of demand
        
        # Generate data for the last 30 days
        for days_back in range(30):
            date = current_date - timedelta(days=days_back)
            
            # Add seasonal and daily variations
            seasonal_factor = 1.0 + 0.15 * np.sin(2 * np.pi * date.timetuple().tm_yday / 365)
            daily_variation = random.uniform(0.85, 1.15)
            
            daily_demand = base_demand * seasonal_factor * daily_variation
            daily_capacity = base_capacity * random.uniform(0.95, 1.05)  # Slight capacity variations
            
            demand_data.append((
                len(demand_data) + 1,
                zone_id,
                round(daily_demand, 2),
                round(daily_capacity, 2),
                date.strftime("%Y-%m-%d")
            ))
    
    return demand_data

def generate_complaints_data():
    """Generate realistic complaint data"""
    complaint_types = ["blockage", "leak", "odor", "damage", "overflow", "backup", "noise"]
    severities = ["low", "medium", "high", "critical"]
    statuses = ["open", "in_progress", "resolved", "closed"]
    
    # NYC coordinate bounds (approximate)
    lat_min, lat_max = 40.4774, 40.9176
    lng_min, lng_max = -74.2591, -73.7004
    
    complaints_data = []
    current_date = datetime.now()
    
    # Generate 150 complaints over the last 90 days
    for i in range(150):
        complaint_date = current_date - timedelta(days=random.randint(0, 90))
        
        complaint_type = random.choice(complaint_types)
        severity = random.choice(severities)
        status = random.choice(statuses)
        
        # Generate realistic descriptions
        descriptions = {
            "blockage": [
                "Severe blockage in main sewer line causing backups",
                "Partial blockage with slow drainage",
                "Complete blockage causing street flooding",
                "Tree roots blocking sewer pipe"
            ],
            "leak": [
                "Sewage leaking from manhole cover",
                "Underground pipe leak detected",
                "Visible sewage seepage in street",
                "Leak causing sinkhole formation"
            ],
            "odor": [
                "Strong sewage odor in residential area",
                "Persistent smell near storm drains",
                "Odor complaints from multiple residents",
                "Chemical smell from treatment facility"
            ],
            "damage": [
                "Collapsed sewer pipe section",
                "Damaged manhole cover",
                "Pipe damage from construction",
                "Infrastructure damage from flooding"
            ],
            "overflow": [
                "Sewage overflow during heavy rain",
                "Treatment plant overflow",
                "Pump station malfunction causing overflow",
                "Combined sewer overflow event"
            ],
            "backup": [
                "Sewage backup in basement",
                "Multiple building backup",
                "Street-level sewage backup",
                "Backup affecting commercial buildings"
            ],
            "noise": [
                "Loud pump station noise",
                "Unusual sounds from underground",
                "Pump malfunction creating noise",
                "Equipment noise complaints"
            ]
        }
        
        description = random.choice(descriptions[complaint_type])
        
        # Weight severity distribution (more low/medium than high/critical)
        severity_weights = {"low": 0.4, "medium": 0.35, "high": 0.2, "critical": 0.05}
        severity = random.choices(list(severity_weights.keys()), weights=list(severity_weights.values()))[0]
        
        complaints_data.append((
            i + 1,
            round(random.uniform(lat_min, lat_max), 6),
            round(random.uniform(lng_min, lng_max), 6),
            complaint_type,
            severity,
            description,
            status,
            complaint_date.strftime("%Y-%m-%d %H:%M:%S"),
            complaint_date.strftime("%Y-%m-%d %H:%M:%S")
        ))
    
    return complaints_data

def generate_illegal_connections_data():
    """Generate realistic illegal connections data"""
    connection_types = ["industrial", "residential", "commercial", "mixed"]
    statuses = ["unverified", "confirmed", "false_positive", "under_investigation"]
    
    # NYC coordinate bounds
    lat_min, lat_max = 40.4774, 40.9176
    lng_min, lng_max = -74.2591, -73.7004
    
    illegal_connections_data = []
    current_date = datetime.now()
    
    # Generate 75 suspected illegal connections
    for i in range(75):
        detection_date = current_date - timedelta(days=random.randint(0, 180))
        
        # Higher confidence for confirmed connections, lower for unverified
        if random.random() < 0.3:  # 30% confirmed
            confidence = random.uniform(0.75, 0.98)
            status = random.choice(["confirmed", "under_investigation"])
        else:  # 70% unverified or false positive
            confidence = random.uniform(0.45, 0.85)
            status = random.choice(["unverified", "false_positive"])
        
        connection_type = random.choice(connection_types)
        
        illegal_connections_data.append((
            i + 1,
            round(random.uniform(lat_min, lat_max), 6),
            round(random.uniform(lng_min, lng_max), 6),
            round(confidence, 3),
            connection_type,
            detection_date.strftime("%Y-%m-%d"),
            status
        ))
    
    return illegal_connections_data

def generate_processed_images_data():
    """Generate sample processed images data"""
    image_statuses = ["completed", "processing", "failed", "queued"]
    
    processed_images_data = []
    current_date = datetime.now()
    
    # Generate 25 processed images
    for i in range(25):
        upload_date = current_date - timedelta(days=random.randint(0, 60))
        
        original_filename = f"satellite_image_{i+1:03d}.{random.choice(['jpg', 'png', 'tif', 'tiff'])}"
        stored_filename = f"stored_{i+1:03d}_{upload_date.strftime('%Y%m%d')}.jpg"
        mask_filename = f"mask_{i+1:03d}_{upload_date.strftime('%Y%m%d')}.png" if random.random() > 0.2 else None
        
        processing_time = round(random.uniform(5.2, 45.8), 2) if random.random() > 0.1 else None
        status = random.choice(image_statuses)
        width = random.choice([1024, 2048, 4096, 8192])
        height = random.choice([1024, 2048, 4096, 8192])
        
        processed_images_data.append((
            i + 1,
            original_filename,
            stored_filename,
            mask_filename,
            upload_date.strftime("%Y-%m-%d %H:%M:%S"),
            processing_time,
            status,
            width,
            height
        ))
    
    return processed_images_data

def insert_comprehensive_data():
    """Insert all comprehensive data into database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Generate all data
        logger.info("Generating comprehensive data...")
        
        zones_data = generate_comprehensive_zones()
        demand_data = generate_demand_data(zones_data)
        complaints_data = generate_complaints_data()
        illegal_connections_data = generate_illegal_connections_data()
        processed_images_data = generate_processed_images_data()
        
        # Insert zones
        logger.info(f"Inserting {len(zones_data)} zones...")
        cursor.executemany(
            "INSERT INTO zones (zone_id, name, district, population, area_sqkm) VALUES (?, ?, ?, ?, ?)",
            zones_data
        )
        
        # Insert demand data
        logger.info(f"Inserting {len(demand_data)} demand records...")
        cursor.executemany(
            "INSERT INTO sewage_demand (id, zone_id, demand_m3, capacity_m3, timestamp) VALUES (?, ?, ?, ?, ?)",
            demand_data
        )
        
        # Insert complaints
        logger.info(f"Inserting {len(complaints_data)} complaints...")
        cursor.executemany(
            "INSERT INTO complaints (id, lat, lng, type, severity, description, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            complaints_data
        )
        
        # Insert illegal connections
        logger.info(f"Inserting {len(illegal_connections_data)} illegal connections...")
        cursor.executemany(
            "INSERT INTO illegal_connections (id, lat, lng, confidence, type, detected_date, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            illegal_connections_data
        )
        
        # Insert processed images
        logger.info(f"Inserting {len(processed_images_data)} processed images...")
        cursor.executemany(
            "INSERT INTO processed_images (id, original_filename, stored_filename, mask_filename, upload_date, processing_time, status, width, height) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            processed_images_data
        )
        
        conn.commit()
        logger.info("All comprehensive data inserted successfully!")
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM zones")
        zones_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM sewage_demand")
        demand_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM complaints")
        complaints_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM illegal_connections")
        illegal_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM processed_images")
        images_count = cursor.fetchone()[0]
        
        print(f"\n=== DATABASE SUMMARY ===")
        print(f"Zones: {zones_count}")
        print(f"Sewage Demand Records: {demand_count}")
        print(f"Complaints: {complaints_count}")
        print(f"Illegal Connections: {illegal_count}")
        print(f"Processed Images: {images_count}")
        print(f"========================\n")
        
    except Exception as e:
        logger.error(f"Error inserting comprehensive data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    # Ensure we're in the right directory
    if not os.path.exists(DATABASE_PATH):
        logger.error(f"Database not found at {DATABASE_PATH}")
        exit(1)
    
    # Clear existing data and insert comprehensive data
    clear_existing_data()
    insert_comprehensive_data()
