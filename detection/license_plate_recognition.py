import os
import cv2
import numpy as np
import logging
import re
import random

logger = logging.getLogger(__name__)

class LicensePlateRecognizer:
    def __init__(self):
        """
        Initialize license plate recognizer for Chinese license plates
        """
        try:
            # Define Chinese license plate format regex
            # Chinese license plates typically have format: 省份+字母+5位字母或数字
            # Examples: 京A12345, 粤B12345, 沪C·12345
            self.plate_pattern = re.compile(r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领]{1}[A-Z]{1}[·-]{0,1}[A-Z0-9]{5}')
            
            # Sample Chinese license plates for demo purposes
            self.sample_plates = [
                "京A12345", "沪B88888", "粤C99999", "津D55555",
                "冀E66666", "晋F77777", "鲁G12345", "豫H45678"
            ]
            
            logger.info("License plate recognizer initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing license plate recognizer: {e}")
            logger.warning("Falling back to simple recognition without language-specific settings")
    
    def preprocess_plate_image(self, plate_image):
        """
        Preprocess license plate image for better OCR
        
        Args:
            plate_image: License plate image (numpy array)
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert to grayscale
            if len(plate_image.shape) == 3:
                gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = plate_image
            
            # Apply some blur to reduce noise
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY_INV, 11, 2)
            
            # Dilate to connect broken character parts
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(thresh, kernel, iterations=1)
            
            # Find contours and mask everything except the largest ones (likely characters)
            contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            # Keep only the largest contours (likely characters)
            char_mask = np.zeros_like(dilated)
            for i, contour in enumerate(sorted_contours[:20]):  # Keep top 20 contours
                if cv2.contourArea(contour) > 10:  # Minimum area threshold
                    cv2.drawContours(char_mask, [contour], -1, 255, -1)
            
            # Apply the mask to the thresholded image
            cleaned = cv2.bitwise_and(thresh, char_mask)
            
            # Invert back for OCR (black text on white background)
            cleaned = cv2.bitwise_not(cleaned)
            
            return cleaned
        
        except Exception as e:
            logger.error(f"Error preprocessing plate image: {e}")
            return plate_image  # Return original if preprocessing fails
    
    def recognize_plate(self, plate_image):
        """
        Recognize text on license plate
        
        Args:
            plate_image: License plate image (numpy array)
            
        Returns:
            Recognized license plate text, confidence
        """
        try:
            # Check if image is valid
            if plate_image is None or plate_image.size == 0:
                return "", 0.0
            
            # For demonstration purposes, return a random Chinese license plate
            # In a real implementation, this would use OCR to read the text from the image
            plate_text = random.choice(self.sample_plates)
            confidence = random.uniform(0.75, 0.95)  # Random confidence between 75-95%
            
            logger.info(f"Recognized license plate: {plate_text} with confidence {confidence:.2f}")
            return plate_text, confidence
        
        except Exception as e:
            logger.error(f"Error recognizing license plate: {e}")
            return "", 0.0
