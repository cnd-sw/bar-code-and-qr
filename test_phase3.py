
from src.detection.barcode_detector import BarcodeDetector
from src.decoding.barcode_decoder import BarcodeDecoder
from src.utils.visualization import draw_detections, save_visualization
from src.utils.file_io import read_image, get_image_annotation_pairs
import random
from pathlib import Path

def test_barcode_pipeline():
    print("Testing Barcode Detection & Decoding Pipeline...")
    
    detector = BarcodeDetector()
    decoder = BarcodeDecoder()
    
    # 1. Test Class 0 (Single/No Barcode) - Pick a reliable one
    # Note: Many files in 0/ are "no barcode", we should pick one that likely has one or check annotations
    # based on exploration, 0/ has images.
    
    base_dir = Path("barcode_data")
    
    # helper to find an image with annotations
    def get_sample(class_dir_name):
        pairs = get_image_annotation_pairs(base_dir / class_dir_name)
        if not pairs:
            return None
        # Pick random sample
        return random.choice(pairs)[0]
    
    sample_0 = get_sample("0")
    sample_1 = get_sample("1")
    
    if not sample_0 or not sample_1:
        print("Could not find samples in barcode_data")
        return False
        
    print(f"Sample Class 0: {sample_0}")
    print(f"Sample Class 1: {sample_1}")
    
    for i, sample_path in enumerate([sample_0, sample_1]):
        print(f"\n--- Testing Sample {i} ({sample_path.name}) ---")
        
        # Load image
        image = read_image(str(sample_path))
        if image is None:
            continue
            
        # 1. Detect using Ground Truth Annotations
        gt_detections = detector.detect(sample_path)
        print(f"Ground Truth Detections: {len(gt_detections)}")
        
        # 2. Decode using pyzbar
        decodings = decoder.decode(str(sample_path))
        print(f"Decoded Barcodes: {len(decodings)}")
        for d in decodings:
            print(f"  Type: {d['barcode_type']}, Data: {d['data']}")
            
        # 3. Visualization strategy
        # If we have decodings, use them. If not, use GT. 
        # Ideally we want to see if GT overlaps with Decoding
        
        final_vis = decodings if decodings else gt_detections
        
        # Mark GT with Blue, Decoded with Green (default)
        vis_image = image.copy()
        
        # Draw GT in Blue
        from src.utils.visualization import draw_bounding_box
        for d in gt_detections:
            vis_image = draw_bounding_box(vis_image, d['bbox'], "GT", (255, 0, 0))
            
        # Draw Decoded in Green
        for d in decodings:
            label = f"{d['barcode_type']}: {d['data']}"
            vis_image = draw_bounding_box(vis_image, d['bbox'], label, (0, 255, 0))
            
        output_path = f"outputs/phase3_test_result_{i}.png"
        save_visualization(vis_image, output_path)
        print(f"Visualization saved to {output_path}")

    return True

if __name__ == "__main__":
    test_barcode_pipeline()
