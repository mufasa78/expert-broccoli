# Initialize the app package
import os
from flask import Flask
from models import db

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create the Flask application instance with proper static and template folders
app = Flask(
    __name__,
    template_folder=os.path.join(project_root, 'templates'),
    static_folder=os.path.join(project_root, 'static'),
    static_url_path='/static'
)

# Import routes after app is created to avoid circular imports
from app import routes