import os
import cv2
import numpy as np
import logging
from typing import Tuple, Dict, Any, List

logger = logging.getLogger(__name__)

def process_image(image_path: str, detection_type: str, yolo_detector, license_plate_recognizer, lane_intrusion_detector) -> Tuple[Dict[str, Any], np.ndarray]:
    """
    Process an image for either license plate recognition or lane intrusion detection
    
    Args:
        image_path: Path to the image file
        detection_type: Type of detection ('license_plate' or 'lane_intrusion')
        yolo_detector: YOLODetector instance
        license_plate_recognizer: LicensePlateRecognizer instance
        lane_intrusion_detector: LaneIntrusionDetector instance
        
    Returns:
        result: Dictionary with detection results
        output_image: Image with detection visualizations
    """
    try:
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Failed to read image from {image_path}")
            return {"error": "Failed to read image"}, np.zeros((100, 100, 3), dtype=np.uint8)
        
        if detection_type == 'license_plate':
            # Detect vehicles
            vehicle_detections = yolo_detector.detect_vehicles(image)
            
            # Detect license plates
            license_plate_detections = yolo_detector.detect_license_plates(image, vehicle_detections)
            
            # Recognize license plates
            output_image = image.copy()
            detections_with_plates = []
            
            for i, lp_detection in enumerate(license_plate_detections):
                x1, y1, x2, y2 = lp_detection['bbox']
                
                # Extract license plate image
                plate_img = image[y1:y2, x1:x2]
                
                # Recognize text on the plate
                plate_text, confidence = license_plate_recognizer.recognize_plate(plate_img)
                
                # Add recognized text to detection
                lp_detection['license_plate'] = plate_text
                lp_detection['confidence'] = confidence
                detections_with_plates.append(lp_detection)
                
                # Draw bounding box and text on the image
                cv2.rectangle(output_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Add background for text
                text_size = cv2.getTextSize(plate_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                cv2.rectangle(output_image, (x1, y1 - 25), (x1 + text_size[0] + 10, y1), (0, 255, 0), -1)
                
                # Add text
                cv2.putText(output_image, plate_text, (x1 + 5, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                
                # Add confidence
                conf_text = f"{confidence:.2f}"
                cv2.putText(output_image, conf_text, (x2 - 40, y2 + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Draw vehicle bounding boxes
            for vehicle in vehicle_detections:
                x1, y1, x2, y2 = vehicle['bbox']
                cv2.rectangle(output_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
            
            result = {
                "detections": detections_with_plates,
                "vehicles": vehicle_detections
            }
            
            return result, output_image
        
        elif detection_type == 'lane_intrusion':
            # Detect vehicles
            vehicle_detections = yolo_detector.detect_vehicles(image)
            
            # Process for lane intrusion
            output_image, intrusions = lane_intrusion_detector.process_frame(image, vehicle_detections)
            
            result = {
                "vehicles": vehicle_detections,
                "intrusions": intrusions
            }
            
            return result, output_image
        
        else:
            logger.error(f"Unknown detection type: {detection_type}")
            return {"error": f"Unknown detection type: {detection_type}"}, image
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return {"error": str(e)}, np.zeros((100, 100, 3), dtype=np.uint8)

def save_detection_result(output_image: np.ndarray, original_filename: str, output_dir: str) -> str:
    """
    Save the detection result image
    
    Args:
        output_image: Image with detection results
        original_filename: Original filename
        output_dir: Directory to save the result
        
    Returns:
        Path to the saved image
    """
    try:
        # Create result filename
        name, ext = os.path.splitext(original_filename)
        result_filename = f"result_{name}{ext}"
        result_path = os.path.join(output_dir, result_filename)
        
        # Save the image
        cv2.imwrite(result_path, output_image)
        
        return result_path
    
    except Exception as e:
        logger.error(f"Error saving detection result: {e}")
        raise
