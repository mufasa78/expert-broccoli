# License Plate Reader

A comprehensive application for license plate detection and recognition with lane intrusion detection capabilities.

## Features

- **License Plate Detection and Recognition**: Detect and recognize license plates in images and videos
- **Lane Intrusion Detection**: Detect vehicles intruding into designated lanes
- **Bilingual Support**: Interface available in both Chinese and English
- **Multiple Interfaces**:
  - Web interface using Flask
  - Streamlit application for interactive usage
- **Database Integration**: Store detection results in PostgreSQL database
- **File Upload**: Support for various image and video formats

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL (Neon)
- **Computer Vision**: OpenCV, YOLOv8
- **OCR**: Custom license plate recognition
- **Interactive UI**: Streamlit

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables (optional):
   ```
   export FLASK_SECRET_KEY=your_secret_key
   ```

## Usage

### Flask Web Application

Run the Flask application:
```
python main.py
```
The application will be available at http://localhost:5000

### Streamlit Interface

Run the Streamlit application:
```
streamlit run streamlit_app.py
```
The Streamlit interface will be available at http://localhost:8501

## Project Structure

- `app/`: Flask application routes and views
- `detection/`: Detection modules (YOLO, license plate recognition, lane intrusion)
- `i18n/`: Internationalization and translation files
- `static/`: Static assets (CSS, JavaScript, images)
- `templates/`: HTML templates for the web interface
- `utils/`: Utility functions
- `main.py`: Flask application entry point
- `streamlit_app.py`: Streamlit application entry point
- `models.py`: Database models
- `config.py`: Application configuration

## License

[Specify your license here]

## Acknowledgements

- YOLOv8 for object detection
- OpenCV for image processing
- Flask and Streamlit for web interfaces
