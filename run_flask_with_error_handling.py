import os
import sys
import traceback
import logging
from datetime import datetime

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"flask_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_flask_app():
    try:
        logger.info("Starting Flask application...")

        # Check if virtual environment is activated
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.warning("Virtual environment is not activated. This may cause issues.")

        # Check if required packages are installed
        required_packages = ['flask', 'flask_sqlalchemy', 'psycopg2', 'numpy']
        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                logger.info(f"Package {package} is installed.")
            except ImportError:
                missing_packages.append(package)
                logger.error(f"Package {package} is not installed.")

        # Special check for OpenCV
        try:
            import cv2
            logger.info("Package opencv-python is installed.")
        except ImportError:
            missing_packages.append('opencv-python')
            logger.error("Package opencv-python is not installed.")

        if missing_packages:
            logger.error(f"Missing required packages: {', '.join(missing_packages)}")
            logger.error("Please install the missing packages using: pip install -r requirements.txt")
            return False

        # Check if database connection is working
        try:
            import psycopg2
            neon_database_url = "postgresql://neondb_owner:npg_Niz38CoUlIcP@ep-curly-waterfall-a4n1iyhv-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
            conn = psycopg2.connect(neon_database_url)
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            logger.info(f"Database connection successful. PostgreSQL version: {version[0]}")
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False

        # Check if templates directory exists
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        if not os.path.exists(templates_dir):
            logger.error(f"Templates directory not found: {templates_dir}")
            return False
        else:
            logger.info(f"Templates directory found: {templates_dir}")
            template_files = os.listdir(templates_dir)
            logger.info(f"Template files: {', '.join(template_files)}")

        # Check if static directory exists
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        if not os.path.exists(static_dir):
            logger.error(f"Static directory not found: {static_dir}")
            return False
        else:
            logger.info(f"Static directory found: {static_dir}")

        # Import the Flask app
        try:
            from main import app
            logger.info("Flask app imported successfully.")
        except Exception as e:
            logger.error(f"Error importing Flask app: {e}")
            logger.error(traceback.format_exc())
            return False

        # Run the Flask app
        logger.info("Running Flask app...")
        app.run(host="0.0.0.0", port=5000, debug=True)

        return True

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = run_flask_app()
    if success:
        logger.info("Flask application started successfully.")
    else:
        logger.error("Failed to start Flask application. Check the logs for details.")
        sys.exit(1)
