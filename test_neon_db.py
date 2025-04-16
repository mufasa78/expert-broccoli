import psycopg2
import sys

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
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    print("Database connection test completed successfully.")
    
except Exception as e:
    print(f"Error connecting to the database: {e}")
    sys.exit(1)
