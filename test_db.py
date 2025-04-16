import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from models import DetectionResult, DetectionItem

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
# setup a secret key, required by sessions
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"

# Use the provided Neon PostgreSQL URL
neon_database_url = "postgresql://neondb_owner:npg_Niz38CoUlIcP@ep-curly-waterfall-a4n1iyhv-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
app.config["SQLALCHEMY_DATABASE_URI"] = neon_database_url

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
# initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

print("Starting database test...")

# Test database connection
with app.app_context():
    try:
        print("Creating tables if they don't exist...")
        db.create_all()
        print("Tables created or already exist.")

        # Try to query the database
        print("Querying database...")
        results = DetectionResult.query.all()
        print(f"Database connection successful. Found {len(results)} detection results.")

        # Create a test record if none exist
        if len(results) == 0:
            print("Creating a test record...")
            test_result = DetectionResult(
                filename="test.jpg",
                detection_type="license_plate",
                result_path="static/results/test_result.jpg"
            )
            db.session.add(test_result)
            db.session.commit()
            print(f"Test record created with ID: {test_result.id}")

            # Create a test detection item
            test_item = DetectionItem(
                detection_id=test_result.id,
                license_plate="京A12345",
                confidence=0.95,
                bbox_x1=100,
                bbox_y1=100,
                bbox_x2=200,
                bbox_y2=150
            )
            db.session.add(test_item)
            db.session.commit()
            print(f"Test detection item created with ID: {test_item.id}")

            # Query again to verify
            results = DetectionResult.query.all()
            print(f"Now have {len(results)} detection results.")

    except Exception as e:
        print(f"Database connection error: {e}")

print("Database test completed.")
