import os
import logging
from flask import render_template, request, jsonify, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import base64
from models import db, DetectionResult, DetectionItem
from i18n.translations import get_text
from detection.yolo_detector import YOLODetector
from detection.license_plate_recognition import LicensePlateRecognizer
from detection.lane_intrusion import LaneIntrusionDetector
from utils.helpers import process_image, save_detection_result

# Get the app instance from app/__init__.py
from app import app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize detectors
yolo_detector = YOLODetector()
license_plate_recognizer = LicensePlateRecognizer()
lane_intrusion_detector = LaneIntrusionDetector()

# Create upload folder if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set the maximum file size (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Set default language to Chinese if not set
    if 'lang' not in session:
        session['lang'] = 'zh'

    return render_template('index.html',
                          title=get_text('app_title', session.get('lang', 'zh')),
                          lang=session.get('lang', 'zh'))

@app.route('/switch_language/<lang>')
def switch_language(lang):
    if lang in ['zh', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash(get_text('no_file_error', session.get('lang', 'zh')), 'danger')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash(get_text('no_file_selected_error', session.get('lang', 'zh')), 'danger')
        return redirect(request.url)

    detection_type = request.form.get('detection_type', 'license_plate')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            if filepath.endswith(('.mp4', '.avi')):
                # Process video (save first frame for preview)
                cap = cv2.VideoCapture(filepath)
                ret, frame = cap.read()
                if ret:
                    preview_path = os.path.join(app.config['UPLOAD_FOLDER'], 'preview_' + filename.rsplit('.', 1)[0] + '.jpg')
                    cv2.imwrite(preview_path, frame)
                    preview_path = preview_path.replace('static/', '')
                else:
                    preview_path = None
                cap.release()

                # Create a detection record in the database
                detection = DetectionResult(
                    filename=filename,
                    detection_type=detection_type,
                    result_path=filepath.replace('static/', '')
                )
                db.session.add(detection)
                db.session.commit()

                flash(get_text('video_processing_start', session.get('lang', 'zh')), 'info')
                return render_template('detection_results.html',
                                      title=get_text('processing_video', session.get('lang', 'zh')),
                                      file_path=filepath.replace('static/', ''),
                                      preview_path=preview_path,
                                      is_video=True,
                                      detection_type=detection_type,
                                      lang=session.get('lang', 'zh'))
            else:
                # Process image
                result, output_image = process_image(filepath, detection_type, yolo_detector,
                                                   license_plate_recognizer, lane_intrusion_detector)

                result_path = save_detection_result(output_image, filename, app.config['UPLOAD_FOLDER'])
                rel_result_path = result_path.replace('static/', '')

                # Create a detection record in the database
                detection = DetectionResult(
                    filename=filename,
                    detection_type=detection_type,
                    result_path=rel_result_path
                )
                db.session.add(detection)
                db.session.flush()  # Get the ID without committing

                # Add detection items
                if detection_type == 'license_plate' and 'detections' in result:
                    for item in result['detections']:
                        if 'license_plate' in item and item['license_plate']:
                            bbox = item.get('bbox', (0, 0, 0, 0))
                            detection_item = DetectionItem(
                                detection_id=detection.id,
                                license_plate=item['license_plate'],
                                confidence=item.get('confidence', 0),
                                bbox_x1=bbox[0],
                                bbox_y1=bbox[1],
                                bbox_x2=bbox[2],
                                bbox_y2=bbox[3]
                            )
                            db.session.add(detection_item)

                elif detection_type == 'lane_intrusion' and 'intrusions' in result:
                    for item in result['intrusions']:
                        detection_item = DetectionItem(
                            detection_id=detection.id,
                            vehicle_id=item.get('vehicle_id'),
                            from_lane=item.get('from_lane'),
                            to_lane=item.get('to_lane'),
                            bbox_x1=item.get('vehicle_bbox', (0, 0, 0, 0))[0],
                            bbox_y1=item.get('vehicle_bbox', (0, 0, 0, 0))[1],
                            bbox_x2=item.get('vehicle_bbox', (0, 0, 0, 0))[2],
                            bbox_y2=item.get('vehicle_bbox', (0, 0, 0, 0))[3]
                        )
                        db.session.add(detection_item)

                db.session.commit()

                return render_template('detection_results.html',
                                      title=get_text('detection_results', session.get('lang', 'zh')),
                                      file_path=rel_result_path,
                                      result=result,
                                      is_video=False,
                                      detection_type=detection_type,
                                      lang=session.get('lang', 'zh'))

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            flash(get_text('processing_error', session.get('lang', 'zh')) + f": {str(e)}", 'danger')
            return redirect(url_for('index'))

    flash(get_text('invalid_file_error', session.get('lang', 'zh')), 'danger')
    return redirect(url_for('index'))

@app.route('/api/detect', methods=['POST'])
def api_detect():
    """API endpoint for detection"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    detection_type = request.form.get('detection_type', 'license_plate')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            if filepath.endswith(('.mp4', '.avi')):
                # For API, we'll process videos frame by frame
                results = []
                cap = cv2.VideoCapture(filepath)
                frame_count = 0

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    frame_count += 1
                    if frame_count % 10 != 0:  # Process every 10th frame to reduce load
                        continue

                    # Save frame temporarily
                    temp_frame_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_frame_{frame_count}.jpg")
                    cv2.imwrite(temp_frame_path, frame)

                    # Process the frame
                    result, _ = process_image(temp_frame_path, detection_type, yolo_detector,
                                             license_plate_recognizer, lane_intrusion_detector)

                    # Add frame info to result
                    result['frame'] = frame_count
                    results.append(result)

                    # Remove temporary frame file
                    os.remove(temp_frame_path)

                cap.release()
                return jsonify({'type': 'video', 'results': results})
            else:
                # Process image
                result, output_image = process_image(filepath, detection_type, yolo_detector,
                                                  license_plate_recognizer, lane_intrusion_detector)

                # Convert output image to base64 for JSON response
                _, buffer = cv2.imencode('.jpg', output_image)
                img_str = base64.b64encode(buffer).decode('utf-8')

                result['image'] = img_str
                return jsonify({'type': 'image', 'result': result})

        except Exception as e:
            logger.error(f"API Error: {e}")
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/process_video', methods=['POST'])
def process_video():
    """Process video file frame by frame and return results"""
    filepath = request.form.get('filepath')
    detection_type = request.form.get('detection_type', 'license_plate')

    if not filepath:
        return jsonify({'error': 'No file path provided'}), 400

    full_path = os.path.join('static', filepath)

    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        results = []
        detections_count = 0

        cap = cv2.VideoCapture(full_path)
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Find the database record for this video
        filename = os.path.basename(filepath)
        detection = DetectionResult.query.filter_by(filename=filename).first()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % 10 != 0:  # Process every 10th frame
                continue

            # Save frame temporarily
            temp_frame_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_frame_{frame_count}.jpg")
            cv2.imwrite(temp_frame_path, frame)

            # Process the frame
            result, output_frame = process_image(temp_frame_path, detection_type, yolo_detector,
                                         license_plate_recognizer, lane_intrusion_detector)

            # Save output frame
            result_path = os.path.join(app.config['UPLOAD_FOLDER'], f"result_frame_{frame_count}.jpg")
            cv2.imwrite(result_path, output_frame)

            # Add frame info to result
            result['frame'] = frame_count
            result['frame_path'] = result_path.replace('static/', '')
            result['progress'] = int((frame_count / total_frames) * 100)

            # Save to database if we have a detection record
            if detection:
                if detection_type == 'license_plate' and 'detections' in result:
                    for item in result['detections']:
                        if 'license_plate' in item and item['license_plate']:
                            detections_count += 1
                            bbox = item.get('bbox', (0, 0, 0, 0))
                            detection_item = DetectionItem(
                                detection_id=detection.id,
                                license_plate=item['license_plate'],
                                confidence=item.get('confidence', 0),
                                bbox_x1=bbox[0],
                                bbox_y1=bbox[1],
                                bbox_x2=bbox[2],
                                bbox_y2=bbox[3]
                            )
                            db.session.add(detection_item)

                elif detection_type == 'lane_intrusion' and 'intrusions' in result:
                    for item in result['intrusions']:
                        detections_count += 1
                        detection_item = DetectionItem(
                            detection_id=detection.id,
                            vehicle_id=item.get('vehicle_id'),
                            from_lane=item.get('from_lane'),
                            to_lane=item.get('to_lane'),
                            bbox_x1=item.get('vehicle_bbox', (0, 0, 0, 0))[0],
                            bbox_y1=item.get('vehicle_bbox', (0, 0, 0, 0))[1],
                            bbox_x2=item.get('vehicle_bbox', (0, 0, 0, 0))[2],
                            bbox_y2=item.get('vehicle_bbox', (0, 0, 0, 0))[3]
                        )
                        db.session.add(detection_item)

            results.append(result)

            # Remove temporary frame file
            os.remove(temp_frame_path)

        cap.release()

        # Commit any database changes
        if detection:
            db.session.commit()

        return jsonify({
            'success': True,
            'results': results,
            'total_frames': total_frames,
            'processed_frames': frame_count,
            'detections_count': detections_count
        })

    except Exception as e:
        logger.error(f"Video processing error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def detection_history():
    """Display detection history from the database"""
    detections = DetectionResult.query.order_by(DetectionResult.created_at.desc()).all()
    return render_template('history.html',
                          title=get_text('detection_history', session.get('lang', 'zh')),
                          detections=detections,
                          lang=session.get('lang', 'zh'))