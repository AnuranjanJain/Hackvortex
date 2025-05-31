import os
import json
import random
import datetime
import numpy as np
import pandas as pd
import sqlite3
from pathlib import Path

# Ensure the data folder exists
if not os.path.exists('data'):
    os.makedirs('data')

# Connect to SQLite database
DB_PATH = 'data/sewagemap.db'

def connect_db():
    """Connect to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_zones_data(n=20):
    """Generate sample zone data"""
    # Create zones data
    zone_data = pd.DataFrame({
        'zone_id': range(1, n+1),
        'name': [f"Zone{i}" for i in range(1, n+1)],
        'district': ['North', 'South', 'East', 'West', 'Central'] * 4,
        'population': np.random.randint(20000, 100000, n),
        'area_sqkm': np.random.uniform(5, 20, n).round(2),
    })
    
    # Save to CSV and database
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Insert into zones table
        zone_data.to_sql('zones', conn, if_exists='replace', index=False)
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving zone data to database: {e}")
    
    # Also save as CSV for reference
    zone_data.to_csv('data/zones.csv', index=False)
    
    print(f"Generated {len(zone_data)} zones")
    return zone_data

def generate_sewage_demand_data(n=20):
    """Generate sample sewage demand data"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Get zones from database
        cursor.execute("SELECT zone_id, population, area_sqkm FROM zones")
        zones = cursor.fetchall()
        
        if not zones:
            print("No zones found in database. Generating zones first.")
            generate_zones_data()
            cursor.execute("SELECT zone_id, population, area_sqkm FROM zones")
            zones = cursor.fetchall()
        
        demands = []
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        for zone in zones:
            # Base demand calculation
            base_demand = zone['population'] * 0.15  # 150 liters per person per day
            
            # Add variance
            demand = round(base_demand * random.uniform(0.9, 1.1))
            
            # Capacity sometimes over/under demand
            capacity_factor = random.uniform(0.9, 1.2)
            capacity = round(demand * capacity_factor)
            
            # Insert into database
            cursor.execute(
                "INSERT INTO sewage_demand (zone_id, demand_m3, capacity_m3, timestamp) VALUES (?, ?, ?, ?)",
                (zone['zone_id'], demand, capacity, current_date)
            )
            
            demands.append({
                'zone_id': zone['zone_id'],
                'demand_m3': demand,
                'capacity_m3': capacity,
                'timestamp': current_date
            })
        
        conn.commit()
        conn.close()
        
        # Save as JSON for reference
        with open('data/sewage_demand.json', 'w') as f:
            json.dump(demands, f, indent=2)
            
        print(f"Generated sewage demand data for {len(demands)} zones")
        return demands
    except Exception as e:
        print(f"Error generating sewage demand data: {e}")
        return []

def generate_complaint_data(n=50):
    """Generate sample geotagged complaints"""
    complaint_types = ['blockage', 'leak', 'odor', 'damage', 'overflow']
    severity_levels = ['low', 'medium', 'high']
    
    # Center coordinates (New York City)
    center_lat = 40.7128
    center_lng = -74.0060
    
    complaints = []
    
    for i in range(1, n+1):
        # Random coordinates within ~2km of center
        lat = center_lat + random.uniform(-0.02, 0.02)
        lng = center_lng + random.uniform(-0.02, 0.02)
        
        # Random type and severity
        complaint_type = random.choice(complaint_types)
        severity = random.choice(severity_levels)
        
        # Generate description based on type
        descriptions = {
            'blockage': [
                "Complete blockage causing overflow",
                "Partial blockage with slow drainage",
                "Sewer backup into basement",
                "Water pooling due to blockage"
            ],
            'leak': [
                "Sewage leaking into street",
                "Small leak from manhole cover",
                "Constant water seepage from pipe",
                "Leak causing pavement damage"
            ],
            'odor': [
                "Strong odor in residential area",
                "Foul smell from drainage system",
                "Persistent sewer odor near restaurant",
                "Gas-like smell from manhole"
            ],
            'damage': [
                "Collapsed pipe section causing sinkholes",
                "Visible crack in main sewage line",
                "Damaged manhole cover",
                "Erosion around sewer access point"
            ],
            'overflow': [
                "Sewage overflow into local creek",
                "System overflowing during rainfall",
                "Constant overflow from manhole",
                "Backup causing street flooding"
            ]
        }
        
        description = random.choice(descriptions[complaint_type])
        
        # Random status
        status = random.choices(
            ['open', 'in_progress', 'resolved'], 
            weights=[0.5, 0.3, 0.2]
        )[0]
        
        # Random dates
        now = datetime.datetime.now()
        days_ago = random.randint(1, 30)
        created_at = (now - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        if status != 'open':
            updated_at = (now - datetime.timedelta(days=random.randint(0, days_ago-1))).strftime("%Y-%m-%d")
        else:
            updated_at = created_at
        
        complaints.append({
            "id": i,
            "lat": lat,
            "lng": lng,
            "type": complaint_type,
            "severity": severity,
            "description": description,
            "status": status,
            "created_at": created_at,
            "updated_at": updated_at
        })
    
    # Save to database
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM complaints")
        
        # Insert new complaints
        for complaint in complaints:
            cursor.execute("""
                INSERT INTO complaints 
                (id, lat, lng, type, severity, description, status, created_at, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                complaint["id"],
                complaint["lat"],
                complaint["lng"],
                complaint["type"],
                complaint["severity"],
                complaint["description"],
                complaint["status"],
                complaint["created_at"],
                complaint["updated_at"]
            ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving complaints to database: {e}")
    
    # Save as JSON for reference
    with open('data/complaints.json', 'w') as f:
        json.dump(complaints, f, indent=2)
    
    print(f"Generated {len(complaints)} complaints")
    return complaints

def generate_illegal_connections(n=30):
    """Generate sample illegal connections data"""
    connection_types = ['residential', 'industrial', 'commercial']
    
    # Center coordinates (New York City)
    center_lat = 40.7128
    center_lng = -74.0060
    
    connections = []
    
    for i in range(1, n+1):
        # Random coordinates within ~3km of center
        lat = center_lat + random.uniform(-0.03, 0.03)
        lng = center_lng + random.uniform(-0.03, 0.03)
        
        # Random type and confidence
        connection_type = random.choice(connection_types)
        confidence = round(random.uniform(0.65, 0.95), 2)
        
        # Random detection date
        now = datetime.datetime.now()
        days_ago = random.randint(1, 60)
        detected_date = (now - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Random status
        status = random.choices(
            ['unverified', 'confirmed', 'dismissed'], 
            weights=[0.6, 0.3, 0.1]
        )[0]
        
        connections.append({
            "id": i,
            "lat": lat,
            "lng": lng,
            "confidence": confidence,
            "type": connection_type,
            "detected_date": detected_date,
            "status": status
        })
    
    # Save to database
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM illegal_connections")
        
        # Insert new connections
        for connection in connections:
            cursor.execute("""
                INSERT INTO illegal_connections 
                (id, lat, lng, confidence, type, detected_date, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                connection["id"],
                connection["lat"],
                connection["lng"],
                connection["confidence"],
                connection["type"],
                connection["detected_date"],
                connection["status"]
            ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving illegal connections to database: {e}")
    
    # Save as JSON for reference
    with open('data/illegal_connections.json', 'w') as f:
        json.dump(connections, f, indent=2)
    
    print(f"Generated {len(connections)} illegal connections")
    return connections

if __name__ == "__main__":
    print("Generating sample data...")
    # Create directory if it doesn't exist
    Path(os.path.dirname(DB_PATH)).mkdir(parents=True, exist_ok=True)
    
    # Generate data
    generate_zones_data(n=10)
    generate_sewage_demand_data()
    generate_complaint_data(n=30)
    generate_illegal_connections(n=20)
    
    print("Sample data generation complete!")
