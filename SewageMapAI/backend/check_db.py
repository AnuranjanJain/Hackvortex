import sqlite3
import os

db_path = 'data/sewagemap.db'
print(f"Checking database at: {os.path.abspath(db_path)}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print('Available tables:', [table[0] for table in tables])
        
        # Count records in each table
        for table in tables:
            table_name = table[0]
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            print(f'{table_name}: {count} records')
            
            # Show sample data for main tables
            if table_name in ['complaints', 'demand_records', 'illegal_connections', 'zones']:
                cursor.execute(f'SELECT * FROM {table_name} LIMIT 2')
                samples = cursor.fetchall()
                if samples:
                    print(f'  Sample from {table_name}: {samples[0][:3]}...')
        
        conn.close()
    except Exception as e:
        print(f"Error accessing database: {e}")
else:
    print('Database file not found at:', db_path)
