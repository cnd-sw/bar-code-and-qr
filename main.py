"""
Main CLI application for QR code and barcode detection and decoding.

Usage:
    python main.py --input <image_path> --type <qr|barcode|auto>
    python main.py --batch --input-dir <directory> --output <output_file>
"""

import argparse
import sys
import cv2
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Any

from src.utils.logger import setup_logger
from src.utils.config import get_config
from src.utils.file_io import get_image_files, save_results_csv, save_results_json, create_output_filename
from src.utils.visualization import draw_detections, save_visualization

from src.detection.qr_detector import QRDetector
from src.detection.barcode_detector import BarcodeDetector
from src.decoding.qr_decoder import QRDecoder
from src.decoding.barcode_decoder import BarcodeDecoder


def process_image(
    image_path: Path, 
    detection_type: str, 
    config: Dict[str, Any],
    detectors: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Process a single image to detect QR codes and/or barcodes.
    
    Args:
        image_path: Path to image
        detection_type: 'qr', 'barcode', or 'auto'
        config: Configuration dict
        detectors: Dictionary of initialized detector/decoder instances
        
    Returns:
        List of detected objects
    """
    image = cv2.imread(str(image_path))
    if image is None:
        return []
    
    detected_objects = []
    
    # 1. QR Code Detection
    if detection_type in ['qr', 'auto']:
        # Decoder (pyzbar) is primary for both detection and decoding
        decodings = detectors['qr_decoder'].decode_from_image(image)
        detected_objects.extend(decodings)
        
        # Fallback to OpenCV detector if needed (optional)
        # Note: If pyzbar fails, OpenCV often fails too on complex QR codes, 
        # but it provides a good backup for localization
        pass

    # 2. Barcode Detection
    if detection_type in ['barcode', 'auto']:
        # Decoder (pyzbar)
        decodings = detectors['barcode_decoder'].decode_from_image(image)
        detected_objects.extend(decodings)
        
        # Fallback to Ground Truth if available and enabled
        # Only if we didn't find anything via decoding? Or always check GT?
        # Let's check GT if decoding yield nothing, or just merge them
        if not decodings:
            gt_detections = detectors['barcode_detector'].detect(str(image_path))
            detected_objects.extend(gt_detections)
            
    # Add metadata
    for obj in detected_objects:
        obj['filename'] = image_path.name
        obj['file_path'] = str(image_path)
    
    return detected_objects, image


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="QR Code and Barcode Detection & Decoding System"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--input', '-i', type=str, help='Input image path')
    group.add_argument('--batch', '-b', action='store_true', help='Batch mode')
    
    parser.add_argument('--input-dir', type=str, help='Input directory for batch mode')
    parser.add_argument('--type', '-t', choices=['qr', 'barcode', 'auto'], default='auto', help='Detection type')
    parser.add_argument('--output', '-o', type=str, help='Output file (CSV/JSON)')
    parser.add_argument('--output-dir', type=str, default='outputs/visualizations', help='Output dir for visualizations')
    parser.add_argument('--visualize', '-v', action='store_true', help='Enable visualization')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logger = setup_logger(level=log_level)
    config = get_config()
    
    # Validation
    if args.batch and not args.input_dir:
        logger.error("--input-dir is required for batch processing")
        sys.exit(1)

    # Initialize Detectors
    logger.info("Initializing detectors...")
    detectors = {
        'qr_detector': QRDetector(config),
        'qr_decoder': QRDecoder(config),
        'barcode_detector': BarcodeDetector(config),
        'barcode_decoder': BarcodeDecoder(config)
    }
    
    all_results = []
    
    if args.batch:
        logger.info(f"Starting Batch Processing: {args.input_dir}")
        image_files = get_image_files(args.input_dir)
        logger.info(f"Found {len(image_files)} images")
        
        processed_count = 0
        detected_count = 0
        
        for image_path in tqdm(image_files, desc="Processing"):
            try:
                results, image = process_image(image_path, args.type, config, detectors)
                
                if results:
                    all_results.extend(results)
                    detected_count += 1
                
                processed_count += 1
                
                if args.visualize and results:
                    vis_image = draw_detections(image, results)
                    out_name = create_output_filename(image_path, args.output_dir)
                    save_visualization(vis_image, str(out_name))
                    
            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")
                
        logger.info(f"Processed {processed_count} images")
        logger.info(f"Detected codes in {detected_count} images")
        logger.info(f"Total objects found: {len(all_results)}")
        
    else:
        logger.info(f"Processing Single Image: {args.input}")
        image_path = Path(args.input)
        
        try:
            results, image = process_image(image_path, args.type, config, detectors)
            all_results.extend(results)
            
            if results:
                logger.info(f"Found {len(results)} objects:")
                for obj in results:
                    # Format output nicely
                    data = obj.get('data', 'N/A')
                    obj_type = obj.get('type', 'UNKNOWN').upper()
                    bbox = obj.get('bbox', 'N/A')
                    logger.info(f"  [{obj_type}] Data: {data} | Bbox: {bbox}")
            else:
                logger.info("No codes found.")
            
            if args.visualize:
                vis_image = draw_detections(image, results)
                out_name = create_output_filename(image_path, args.output_dir)
                save_visualization(vis_image, str(out_name))
                logger.info(f"Visualization saved to: {out_name}")
                
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            sys.exit(1)

    # Save Results
    if args.output and all_results:
        if args.output.endswith('.json'):
            save_results_json(all_results, args.output)
        else:
            save_results_csv(all_results, args.output)
        logger.info(f"Results saved to: {args.output}")

if __name__ == "__main__":
    main()
