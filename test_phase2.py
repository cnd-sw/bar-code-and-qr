
from src.detection.qr_detector import QRDetector
from src.decoding.qr_decoder import QRDecoder
from src.utils.visualization import draw_detections, display_image, save_visualization, yolo_to_bbox
from src.utils.file_io import read_image
import cv2
import sys
from pathlib import Path

def test_qr_pipeline():
    print("Testing QR Code Detection & Decoding Pipeline...")
    
    # Initialize
    try:
        detector = QRDetector()
        decoder = QRDecoder()
        print("Initialized QRDetector and QRDecoder")
    except Exception as e:
        print(f"Initialization failed: {e}")
        return False
    
    # Load image
    image_path = "qr_data/1002-v1.png" # Standard sample
    image = read_image(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
        return False
        
    # 1. Detect using OpenCV
    print("\n--- Step 1: OpenCV Detection ---")
    detections = detector.detect_from_image(image)
    print(f"Detected {len(detections)} codes")
    for d in detections:
        print(f"  Bbox: {d['bbox']}")
        
    # 2. Decode using pyzbar
    print("\n--- Step 2: pyzbar Decoding ---")
    decodings = decoder.decode_from_image(image)
    print(f"Decoded {len(decodings)} codes")
    for d in decodings:
        print(f"  Data: {d['data']}")
        print(f"  Bbox: {d['bbox']}")
        
    # 3. Visualize
    print("\n--- Step 3: Visualization ---")
    
    # Merge results (prefer decoding results as they have data)
    final_results = decodings 
    if not final_results and detections:
        # If pyzbar failed but OpenCV found something, visualize that
        print("Note: Using OpenCV detections only (no data decoded)")
        final_results = detections
        
    vis_image = draw_detections(image, final_results)
    
    output_path = "outputs/phase2_test_result.png"
    save_visualization(vis_image, output_path)
    print(f"Visualization saved to {output_path}")
    
    return True

if __name__ == "__main__":
    test_qr_pipeline()
