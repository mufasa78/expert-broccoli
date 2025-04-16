import os
from models import db

# Import the app from app/__init__.py
from app import app

# Configure the app
def configure_app(app):
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

    with app.app_context():
        # Create all tables
        db.create_all()

    return app

# Configure the Flask application
app = configure_app(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)