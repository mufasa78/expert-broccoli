import psycopg2
import sys

# Neon PostgreSQL connection string
neon_database_url = "postgresql://neondb_owner:npg_Niz38CoUlIcP@ep-curly-waterfall-a4n1iyhv-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

print("Creating tables in Neon PostgreSQL database...")

try:
    # Connect to the database
    conn = psycopg2.connect(neon_database_url)
    
    # Create a cursor
    cur = conn.cursor()
    
    # Create the detection_result table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS detection_result (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            detection_type VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            result_path VARCHAR(255)
        )
    """)
    
    # Create the detection_item table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS detection_item (
            id SERIAL PRIMARY KEY,
            detection_id INTEGER REFERENCES detection_result(id) ON DELETE CASCADE,
            license_plate VARCHAR(20),
            confidence FLOAT,
            vehicle_id INTEGER,
            from_lane INTEGER,
            to_lane INTEGER,
            bbox_x1 INTEGER,
            bbox_y1 INTEGER,
            bbox_x2 INTEGER,
            bbox_y2 INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Commit the changes
    conn.commit()
    
    # Check if our tables exist
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    tables = cur.fetchall()
    print(f"Found {len(tables)} tables in the database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    print("Tables created successfully.")
    
except Exception as e:
    print(f"Error creating tables: {e}")
    sys.exit(1)
