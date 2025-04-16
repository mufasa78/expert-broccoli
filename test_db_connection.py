import psycopg2
import sys
import time

# Neon PostgreSQL connection string
neon_database_url = "postgresql://neondb_owner:npg_Niz38CoUlIcP@ep-curly-waterfall-a4n1iyhv-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

print("Testing connection to Neon PostgreSQL database...")

try:
    # Connect to the database
    conn = psycopg2.connect(neon_database_url)
    
    # Create a cursor
    cur = conn.cursor()
    
    # Execute a simple query
    cur.execute("SELECT version();")
    
    # Fetch the result
    version = cur.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
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
    
    # If no tables exist, create them
    if len(tables) == 0:
        print("Creating tables...")
        
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
        
        print("Tables created successfully.")
    
    # Insert a test record
    print("Inserting a test record...")
    cur.execute("""
        INSERT INTO detection_result (filename, detection_type, result_path)
        VALUES ('test.jpg', 'license_plate', 'static/results/test_result.jpg')
        RETURNING id
    """)
    
    detection_id = cur.fetchone()[0]
    
    # Insert a test detection item
    cur.execute("""
        INSERT INTO detection_item (
            detection_id, license_plate, confidence, 
            bbox_x1, bbox_y1, bbox_x2, bbox_y2
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (detection_id, '京A12345', 0.95, 100, 100, 200, 150))
    
    item_id = cur.fetchone()[0]
    
    # Commit the changes
    conn.commit()
    
    print(f"Test record created with ID: {detection_id}")
    print(f"Test detection item created with ID: {item_id}")
    
    # Query the data to verify
    cur.execute("""
        SELECT dr.id, dr.filename, dr.detection_type, di.license_plate, di.confidence
        FROM detection_result dr
        JOIN detection_item di ON dr.id = di.detection_id
        ORDER BY dr.created_at DESC
        LIMIT 5
    """)
    
    results = cur.fetchall()
    print(f"\nRecent detection results ({len(results)}):")
    for result in results:
        print(f"  - ID: {result[0]}, Filename: {result[1]}, Type: {result[2]}, Plate: {result[3]}, Confidence: {result[4]:.2f}")
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    print("\nDatabase connection test completed successfully.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
