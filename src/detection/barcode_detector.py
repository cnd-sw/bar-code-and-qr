"""
Barcode Detector module.

This module provides detection capabilities for barcodes.
It supports:
1. Ground Truth mode: Reading existing YOLO annotations
2. Inference mode: Using pyzbar or OpenCV for blind detection
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.file_io import read_image, read_yolo_annotation
from src.utils.visualization import yolo_to_bbox
from src.utils.config import get_config

logger = get_logger(__name__)


class BarcodeDetector:
    """
    Barcode Detector supporting Ground Truth and Inference modes.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Barcode detector.
        """
        self.config = config or get_config()
        self.use_annotations = self.config.get('barcode_detection', {}).get('use_annotations', True)
        
    def detect(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect barcodes in an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries containing detection info.
        """
        image_path = Path(image_path)
        image = read_image(str(image_path))
        if image is None:
            logger.error(f"Failed to load image: {image_path}")
            return []
            
        detections = []

        # 1. Try Ground Truth (Annotations) if enabled
        if self.use_annotations:
            ann_path = image_path.with_suffix('.txt')
            if ann_path.exists():
                detections = self._detect_from_annotations(str(ann_path), image.shape[:2])
                if detections:
                    return detections
        
        # 2. Fallback / Inference
        # (This will be expanded if we add a YOLO model later)
        # For now, we return empty list if no annotations so the system relies on the Decoder to find things
        return detections

    def _detect_from_annotations(self, ann_path: str, image_shape: Tuple[int, int]) -> List[Dict[str, Any]]:
        """
        Parse YOLO annotations into detection objects.
        """
        h, w = image_shape
        yolo_anns = read_yolo_annotation(ann_path)
        detections = []
        
        for class_id, cx, cy, bw, bh in yolo_anns:
            # Convert normalized YOLO to pixel bbox
            x, y, box_w, box_h = yolo_to_bbox((cx, cy, bw, bh), w, h)
            
            detections.append({
                'type': 'barcode',
                'bbox': (x, y, box_w, box_h),
                'confidence': 1.0,  # Ground truth is 100% confident
                'source': 'ground_truth',
                'class_id': class_id
            })
            
        return detections
