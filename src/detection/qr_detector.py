"""
QR Code Detector module.

This module provides detection capabilities for QR codes using OpenCV.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.file_io import read_image
from src.utils.config import get_config

logger = get_logger(__name__)


class QRDetector:
    """
    QR Code Detector using OpenCV.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the QR detector.
        
        Args:
            config: Configuration dictionary. If None, loads from global config.
        """
        self.config = config or get_config()
        self.qr_detector = cv2.QRCodeDetector()
        
    def detect(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect QR codes in an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries containing detection info:
            [
                {
                    'type': 'qr',
                    'bbox': (x, y, w, h),
                    'confidence': float,
                    'raw_bbox': numpy array of points
                }
            ]
        """
        image = read_image(image_path)
        if image is None:
            logger.error(f"Failed to load image: {image_path}")
            return []
            
        return self.detect_from_image(image)

    def detect_from_image(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect QR codes in a loaded CV2 image.
        
        Args:
            image: Numpy array containing the image
            
        Returns:
            List of detection results
        """
        detections = []
        
        try:
            # OpenCV's detectAndDecodeMulti returns:
            # retval (bool), decoded_info (list), points (list), straight_qrcode (list)
            retval, decoded_info, points, _ = self.qr_detector.detectAndDecodeMulti(image)
            
            if retval and points is not None:
                for i, point_set in enumerate(points):
                    # Point set is 4 corners of QR code
                    point_set = point_set.astype(int)
                    
                    # Calculate bounding box from points
                    x, y, w, h = cv2.boundingRect(point_set)
                    
                    # Store detection
                    detections.append({
                        'type': 'qr',
                        'bbox': (int(x), int(y), int(w), int(h)),
                        'confidence': 1.0,  # OpenCV doesn't give confidence, assume 1.0 if detected
                        'raw_bbox': point_set,
                        'data': decoded_info[i] if i < len(decoded_info) else ""
                    })
                    
        except Exception as e:
            logger.error(f"Error during QR detection: {e}")
            
        return detections

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Apply preprocessing to improve detection.
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Optional: Apply histogram equalization or thresholding based on config
        # This will be refined in later steps
        
        return gray
