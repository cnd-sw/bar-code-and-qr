"""
Barcode Decoder module.

This module provides decoding capabilities for various barcode formats using pyzbar.
"""

import os
import platform
import ctypes
from pathlib import Path

# Fix for macOS Homebrew install of zbar
if platform.system() == 'Darwin':
    try:
        paths = [
            '/opt/homebrew/lib/libzbar.dylib',
            '/usr/local/lib/libzbar.dylib'
        ]
        for path in paths:
            if Path(path).exists():
                ctypes.CDLL(path)
                break
    except Exception as e:
        pass

from pyzbar.pyzbar import decode, ZBarSymbol
import numpy as np
from typing import List, Dict, Any
from PIL import Image

from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger(__name__)


class BarcodeDecoder:
    """
    Barcode Decoder using pyzbar.
    Supports EAN, UPC, Code128, Code39, etc.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Barcode decoder.
        """
        self.config = config or get_config()
        
    def decode(self, image_path: str, detections: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Decode barcodes in an image.
        """
        try:
            image = Image.open(image_path)
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return []
            
        return self.decode_from_image(image)
        
    def decode_from_image(self, image: Any) -> List[Dict[str, Any]]:
        """
        Decode barcodes from a PIL or CV2 image.
        """
        results = []
        
        try:
            # We explicitly exclude QRCODE to focus on linear barcodes unless configured otherwise
            # But usually it's fine to detect everything unless performance is an issue
            # Let's detect everything BUT QR codes to keep concerns successful 
            # (or everything if mixed)
            
            # Using all symbols except QRCODE
            # distinct_symbols = set(ZBarSymbol) - {ZBarSymbol.QRCODE}
             # pyzbar API is a bit tricky with lists of symbols, usually it's better to just decode everything
             # and filter by type in the result loop
             
            decoded_objects = decode(image)
            
            for obj in decoded_objects:
                obj_type = obj.type
                
                # Filter out QR codes (handled by QRDecoder)
                if obj_type == 'QRCODE':
                    continue
                    
                data = obj.data.decode('utf-8')
                rect = obj.rect
                polygon = obj.polygon
                
                results.append({
                    'type': 'barcode',
                    'barcode_type': obj_type,
                    'data': data,
                    'bbox': (rect.left, rect.top, rect.width, rect.height),
                    'polygon': [(p.x, p.y) for p in polygon],
                    'orientation': obj.orientation,
                    'quality': obj.quality if hasattr(obj, 'quality') else None
                })
                
        except Exception as e:
            logger.error(f"Error during barcode decoding: {e}")
            
        return results
