"""
QR Code and Barcode Detection & Decoding System

This package provides tools for detecting and decoding QR codes and barcodes
from images using computer vision and machine learning techniques.
"""

__version__ = "1.0.0"
__author__ = "Chandan"

# These will be imported once implemented in Phase 2-4
from src.detection.qr_detector import QRDetector
from src.detection.barcode_detector import BarcodeDetector
from src.decoding.qr_decoder import QRDecoder
from src.decoding.barcode_decoder import BarcodeDecoder

__all__ = [
    "QRDetector",
    "BarcodeDetector",
    "QRDecoder",
    "BarcodeDecoder",
]
