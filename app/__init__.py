# Initialize the app package
import os
from flask import Flask
from models import db

# Create the Flask application instance
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))

# Import routes after app is created to avoid circular imports
from app import routes