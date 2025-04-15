import cv2
import numpy as np
import logging
import time

logger = logging.getLogger(__name__)

class LaneIntrusionDetector:
    def __init__(self):
        """Initialize lane intrusion detector"""
        self.prev_detections = []
        self.detection_history = {}  # Vehicle tracking history
        self.next_id = 1  # ID counter for tracked vehicles
        self.lane_regions = []  # List of lane polygons
        self.intrusion_log = []  # Log of intrusion events
    
    def define_lanes(self, image, method='auto'):
        """
        Define lane regions in the image
        
        Args:
            image: Input image
            method: 'auto' for automatic detection, 'manual' for predefined lanes
            
        Returns:
            List of lane polygons
        """
        h, w = image.shape[:2]
        
        if method == 'auto':
            try:
                # Convert to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Apply Gaussian blur
                blur = cv2.GaussianBlur(gray, (5, 5), 0)
                
                # Apply Canny edge detection
                edges = cv2.Canny(blur, 50, 150)
                
                # Apply Hough line transform
                lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=50)
                
                if lines is None:
                    logger.warning("No lines detected in the image, using manual method")
                    return self.define_lanes(image, 'manual')
                
                # Group lines by slope (to separate left and right lane lines)
                left_lines = []
                right_lines = []
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    if x2 - x1 == 0:  # Avoid division by zero
                        continue
                    
                    slope = (y2 - y1) / (x2 - x1)
                    
                    # Filter out horizontal lines
                    if abs(slope) < 0.3:
                        continue
                    
                    if slope < 0:
                        left_lines.append(line[0])
                    else:
                        right_lines.append(line[0])
                
                if not left_lines or not right_lines:
                    logger.warning("Insufficient lane lines detected, using manual method")
                    return self.define_lanes(image, 'manual')
                
                # Average left and right lines
                def average_lines(lines):
                    x1_sum, y1_sum, x2_sum, y2_sum = 0, 0, 0, 0
                    for x1, y1, x2, y2 in lines:
                        x1_sum += x1
                        y1_sum += y1
                        x2_sum += x2
                        y2_sum += y2
                    n = len(lines)
                    return [int(x1_sum/n), int(y1_sum/n), int(x2_sum/n), int(y2_sum/n)]
                
                left_line = average_lines(left_lines)
                right_line = average_lines(right_lines)
                
                # Create lane polygons from the lines
                x1_left, y1_left, x2_left, y2_left = left_line
                x1_right, y1_right, x2_right, y2_right = right_line
                
                # Extend lines to the bottom of the image
                if y1_left != y2_left:
                    slope_left = (x2_left - x1_left) / (y2_left - y1_left)
                    x1_left_ext = int(x1_left + slope_left * (h - y1_left))
                    x2_left_ext = int(x2_left + slope_left * (0 - y2_left))
                else:
                    x1_left_ext, x2_left_ext = x1_left, x2_left
                
                if y1_right != y2_right:
                    slope_right = (x2_right - x1_right) / (y2_right - y1_right)
                    x1_right_ext = int(x1_right + slope_right * (h - y1_right))
                    x2_right_ext = int(x2_right + slope_right * (0 - y2_right))
                else:
                    x1_right_ext, x2_right_ext = x1_right, x2_right
                
                # Define lane regions (assuming 3 lanes for now)
                lane_width = (x1_right_ext - x1_left_ext) // 3
                
                self.lane_regions = [
                    np.array([
                        [x1_left_ext, h],
                        [x1_left_ext + lane_width, h],
                        [x2_left_ext + lane_width, 0],
                        [x2_left_ext, 0]
                    ], dtype=np.int32),
                    np.array([
                        [x1_left_ext + lane_width, h],
                        [x1_left_ext + 2*lane_width, h],
                        [x2_left_ext + 2*lane_width, 0],
                        [x2_left_ext + lane_width, 0]
                    ], dtype=np.int32),
                    np.array([
                        [x1_left_ext + 2*lane_width, h],
                        [x1_right_ext, h],
                        [x2_right_ext, 0],
                        [x2_left_ext + 2*lane_width, 0]
                    ], dtype=np.int32)
                ]
                
                return self.lane_regions
            
            except Exception as e:
                logger.error(f"Error in automatic lane detection: {e}")
                logger.warning("Falling back to manual lane definition")
                return self.define_lanes(image, 'manual')
        
        else:  # manual method
            # Define simple lanes dividing the image into 3 vertical sections
            lane_width = w // 3
            
            self.lane_regions = [
                np.array([[0, h], [lane_width, h], [lane_width, 0], [0, 0]], dtype=np.int32),
                np.array([[lane_width, h], [2*lane_width, h], [2*lane_width, 0], [lane_width, 0]], dtype=np.int32),
                np.array([[2*lane_width, h], [w, h], [w, 0], [2*lane_width, 0]], dtype=np.int32)
            ]
            
            return self.lane_regions
    
    def assign_vehicle_to_lane(self, vehicle_bbox):
        """
        Determine which lane a vehicle belongs to
        
        Args:
            vehicle_bbox: Vehicle bounding box (x1, y1, x2, y2)
            
        Returns:
            Lane index (0, 1, 2) or -1 if not in any lane
        """
        x1, y1, x2, y2 = vehicle_bbox
        
        # Use bottom center point of the vehicle
        vehicle_point = (x1 + (x2 - x1) // 2, y2)
        
        for i, lane in enumerate(self.lane_regions):
            if cv2.pointPolygonTest(lane, vehicle_point, False) >= 0:
                return i
        
        return -1  # Not in any lane
    
    def track_vehicles(self, detections):
        """
        Track vehicles across frames to detect lane changes
        
        Args:
            detections: List of vehicle detections with bounding boxes
            
        Returns:
            Updated detections with tracking IDs and lane assignments
        """
        if not self.prev_detections:
            # First frame, assign new IDs to all vehicles
            for i, det in enumerate(detections):
                vehicle_id = self.next_id
                self.next_id += 1
                
                lane_idx = self.assign_vehicle_to_lane(det['bbox'])
                
                detections[i]['id'] = vehicle_id
                detections[i]['lane'] = lane_idx
                
                # Initialize tracking history
                self.detection_history[vehicle_id] = {
                    'timestamps': [time.time()],
                    'positions': [det['bbox']],
                    'lanes': [lane_idx]
                }
            
            self.prev_detections = detections
            return detections
        
        # Match current detections with previous ones based on IOU
        updated_detections = []
        matched_prev_ids = set()
        
        for det in detections:
            best_match = None
            best_iou = 0.3  # IOU threshold
            
            for prev_det in self.prev_detections:
                if prev_det['id'] in matched_prev_ids:
                    continue
                
                iou = self.calculate_iou(det['bbox'], prev_det['bbox'])
                
                if iou > best_iou:
                    best_iou = iou
                    best_match = prev_det
            
            if best_match:
                # Match found, update track
                vehicle_id = best_match['id']
                matched_prev_ids.add(vehicle_id)
                
                lane_idx = self.assign_vehicle_to_lane(det['bbox'])
                
                det['id'] = vehicle_id
                det['lane'] = lane_idx
                
                # Update tracking history
                if vehicle_id in self.detection_history:
                    self.detection_history[vehicle_id]['timestamps'].append(time.time())
                    self.detection_history[vehicle_id]['positions'].append(det['bbox'])
                    self.detection_history[vehicle_id]['lanes'].append(lane_idx)
                else:
                    # Shouldn't happen, but handle it anyway
                    self.detection_history[vehicle_id] = {
                        'timestamps': [time.time()],
                        'positions': [det['bbox']],
                        'lanes': [lane_idx]
                    }
            else:
                # New vehicle
                vehicle_id = self.next_id
                self.next_id += 1
                
                lane_idx = self.assign_vehicle_to_lane(det['bbox'])
                
                det['id'] = vehicle_id
                det['lane'] = lane_idx
                
                # Initialize tracking history
                self.detection_history[vehicle_id] = {
                    'timestamps': [time.time()],
                    'positions': [det['bbox']],
                    'lanes': [lane_idx]
                }
            
            updated_detections.append(det)
        
        self.prev_detections = updated_detections
        return updated_detections
    
    def calculate_iou(self, bbox1, bbox2):
        """Calculate Intersection over Union for two bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection area
        x_left = max(x1_1, x1_2)
        y_top = max(y1_1, y1_2)
        x_right = min(x2_1, x2_2)
        y_bottom = min(y2_1, y2_2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculate union area
        bbox1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        bbox2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        
        union_area = bbox1_area + bbox2_area - intersection_area
        
        # Calculate IOU
        iou = intersection_area / union_area if union_area > 0 else 0
        
        return iou
    
    def detect_lane_intrusions(self, tracked_vehicles):
        """
        Detect lane intrusions based on vehicle tracking history
        
        Args:
            tracked_vehicles: List of tracked vehicles with lane assignments
            
        Returns:
            List of intrusion events
        """
        intrusions = []
        
        for vehicle in tracked_vehicles:
            vehicle_id = vehicle['id']
            current_lane = vehicle['lane']
            
            # Skip vehicles not assigned to a lane
            if current_lane == -1:
                continue
            
            # Check history for lane changes
            if vehicle_id in self.detection_history:
                history = self.detection_history[vehicle_id]
                
                # Need at least 2 points to detect a lane change
                if len(history['lanes']) >= 2:
                    previous_lane = history['lanes'][-2]
                    
                    # If the lane changed, log it as an intrusion
                    if previous_lane != current_lane and previous_lane != -1 and current_lane != -1:
                        # Get timestamp of the event
                        timestamp = history['timestamps'][-1]
                        
                        intrusion = {
                            'vehicle_id': vehicle_id,
                            'timestamp': timestamp,
                            'from_lane': previous_lane,
                            'to_lane': current_lane,
                            'vehicle_bbox': vehicle['bbox']
                        }
                        
                        intrusions.append(intrusion)
                        self.intrusion_log.append(intrusion)
        
        return intrusions
    
    def draw_lanes(self, image, lane_colors=None):
        """
        Draw lane markings on the image
        
        Args:
            image: Input image
            lane_colors: List of BGR colors for each lane
            
        Returns:
            Image with lane markings
        """
        if not self.lane_regions:
            self.define_lanes(image)
        
        if lane_colors is None:
            lane_colors = [
                (0, 255, 0),    # Green
                (0, 255, 255),  # Yellow
                (0, 0, 255)     # Red
            ]
        
        lane_img = image.copy()
        
        for i, lane in enumerate(self.lane_regions):
            color = lane_colors[i % len(lane_colors)]
            cv2.polylines(lane_img, [lane], True, color, 2)
            
            # Add lane number
            moments = cv2.moments(lane)
            if moments["m00"] != 0:
                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])
                cv2.putText(lane_img, f"Lane {i+1}", (cx-40, cy), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        return lane_img
    
    def process_frame(self, image, vehicle_detections):
        """
        Process a frame to detect lane intrusions
        
        Args:
            image: Input image
            vehicle_detections: List of vehicle detections
            
        Returns:
            Processed image with lane markings and intrusion alerts,
            List of intrusion events
        """
        # Define lanes if not already done
        if not self.lane_regions:
            self.define_lanes(image)
        
        # Draw lanes on image
        result_img = self.draw_lanes(image)
        
        # Track vehicles
        tracked_vehicles = self.track_vehicles(vehicle_detections)
        
        # Detect lane intrusions
        intrusions = self.detect_lane_intrusions(tracked_vehicles)
        
        # Draw vehicles and their tracks
        for vehicle in tracked_vehicles:
            x1, y1, x2, y2 = vehicle['bbox']
            vehicle_id = vehicle['id']
            lane_idx = vehicle['lane']
            
            # Color based on lane
            if lane_idx == -1:
                color = (128, 128, 128)  # Gray for not in a lane
            else:
                colors = [(0, 255, 0), (0, 255, 255), (0, 0, 255)]
                color = colors[lane_idx % len(colors)]
            
            # Draw bounding box
            cv2.rectangle(result_img, (x1, y1), (x2, y2), color, 2)
            
            # Draw ID and lane
            lane_text = f"Lane {lane_idx+1}" if lane_idx != -1 else "No Lane"
            cv2.putText(result_img, f"ID: {vehicle_id}", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.putText(result_img, lane_text, (x1, y1-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw track
            if vehicle_id in self.detection_history:
                positions = self.detection_history[vehicle_id]['positions']
                if len(positions) > 1:
                    points = []
                    for pos in positions[-10:]:  # Last 10 positions
                        center_x = pos[0] + (pos[2] - pos[0]) // 2
                        center_y = pos[3]  # Bottom center
                        points.append((center_x, center_y))
                    
                    for i in range(1, len(points)):
                        cv2.line(result_img, points[i-1], points[i], color, 2)
        
        # Mark intrusions
        for intrusion in intrusions:
            x1, y1, x2, y2 = intrusion['vehicle_bbox']
            
            # Draw red alert box
            cv2.rectangle(result_img, (x1-5, y1-5), (x2+5, y2+5), (0, 0, 255), 3)
            
            # Draw alert text
            alert_text = f"LANE INTRUSION: {intrusion['from_lane']+1} -> {intrusion['to_lane']+1}"
            cv2.putText(result_img, alert_text, (x1, y1-50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return result_img, intrusions
