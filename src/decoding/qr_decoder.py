"""
QR Code Decoder module.

This module provides decoding capabilities for QR codes using pyzbar.
"""

import os
import platform
import ctypes
from pathlib import Path

# Fix for macOS Homebrew install of zbar
if platform.system() == 'Darwin':
    try:
        # Common Homebrew paths
        paths = [
            '/opt/homebrew/lib/libzbar.dylib',
            '/usr/local/lib/libzbar.dylib'
        ]
        for path in paths:
            if Path(path).exists():
                # Pre-load the library
                ctypes.CDLL(path)
                break
    except Exception as e:
        pass  # Just try to continue if this fails

from pyzbar.pyzbar import decode, ZBarSymbol
import numpy as np
from typing import List, Dict, Any
from PIL import Image

from src.utils.logger import get_logger
from src.utils.file_io import read_image
from src.utils.config import get_config

logger = get_logger(__name__)


class QRDecoder:
    """
    QR Code Decoder using pyzbar.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the QR decoder.
        
        Args:
            config: Configuration dictionary. If None, loads from global config.
        """
        self.config = config or get_config()
        
    def decode(self, image_path: str, detections: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Decode QR codes in an image.
        
        Args:
            image_path: Path to the image file
            detections: Optional list of pre-detected regions to focus on (not used by pyzbar directly but good for interface)
            
        Returns:
            List of dictionaries containing decoded info:
            [
                {
                    'type': 'qr',
                    'data': str,
                    'bbox': (x, y, w, h),
                    'polygon': list of points
                }
            ]
        """
        # pyzbar prefers PIL images
        try:
            image = Image.open(image_path)
        except Exception as e:
            logger.error(f"Failed to load image for decoding: {e}")
            return []
            
        return self.decode_from_image(image)
        
    def decode_from_image(self, image: Any) -> List[Dict[str, Any]]:
        """
        Decode QR codes/barcodes from a PIL or CV2 image.
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            List of decoding results
        """
        results = []
        
        try:
            # Detect ONLY QR codes
            decoded_objects = decode(image, symbols=[ZBarSymbol.QRCODE])
            
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')
                rect = obj.rect
                polygon = obj.polygon
                
                results.append({
                    'type': 'qr',
                    'data': data,
                    'bbox': (rect.left, rect.top, rect.width, rect.height),
                    'polygon': [(p.x, p.y) for p in polygon],
                    'orientation': obj.orientation,
                    'quality': obj.quality if hasattr(obj, 'quality') else None
                })
                
        except Exception as e:
            logger.error(f"Error during QR decoding: {e}")
            # If zbar library is missing, this will fail.
            logger.error("Ensure zbar shared library is installed (brew install zbar on macOS)")
            
        return results

    def combine_results(self, detections: List[Dict], decodings: List[Dict]) -> List[Dict]:
        """
        Combine OpenCV detections with pyzbar decodings.
        This helps when one method sees something the other misses.
        """
        # For now, we'll primarily use pyzbar's results as they contain both location and data
        return decodings
