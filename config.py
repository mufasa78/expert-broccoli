import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Directory for static files
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Directory for uploaded files
UPLOAD_DIR = os.path.join(STATIC_DIR, 'uploads')

# Directory for detection results
RESULTS_DIR = os.path.join(STATIC_DIR, 'results')

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# YOLOv8 settings
YOLO_MODEL = 'yolov8n.pt'  # Default model

# License plate recognition settings
MIN_PLATE_CONFIDENCE = 0.4  # Minimum confidence for license plate recognition

# Lane intrusion detection settings
MIN_VEHICLE_CONFIDENCE = 0.5  # Minimum confidence for vehicle detection

# Flask settings
DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY', 'default_development_key')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

# Streamlit settings
STREAMLIT_PORT = 8501
