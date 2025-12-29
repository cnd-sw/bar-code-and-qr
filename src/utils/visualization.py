"""
Visualization utilities for drawing bounding boxes and labels on images.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from src.utils.config import get_config


def draw_bounding_box(
    image: np.ndarray,
    bbox: Tuple[int, int, int, int],
    label: str = "",
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
    font_scale: float = 0.6,
    font_thickness: int = 2
) -> np.ndarray:
    """
    Draw a bounding box and label on an image.
    
    Args:
        image: Input image (BGR format)
        bbox: Bounding box coordinates (x, y, width, height)
        label: Text label to display
        color: Box color in BGR format
        thickness: Box line thickness
        font_scale: Font size scale
        font_thickness: Font line thickness
        
    Returns:
        Image with bounding box drawn
    """
    x, y, w, h = bbox
    
    # Draw rectangle
    cv2.rectangle(image, (x, y), (x + w, y + h), color, thickness)
    
    # Draw label if provided
    if label:
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness
        )
        
        # Draw background rectangle for text
        cv2.rectangle(
            image,
            (x, y - text_height - baseline - 5),
            (x + text_width, y),
            color,
            -1
        )
        
        # Draw text
        cv2.putText(
            image,
            label,
            (x, y - baseline - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            font_thickness
        )
    
    return image


def draw_detections(
    image: np.ndarray,
    detections: List[Dict[str, Any]],
    color: Optional[Tuple[int, int, int]] = None,
    thickness: Optional[int] = None,
    font_scale: Optional[float] = None,
    font_thickness: Optional[int] = None
) -> np.ndarray:
    """
    Draw multiple detections on an image.
    
    Args:
        image: Input image (BGR format)
        detections: List of detection dictionaries with 'bbox' and 'label' keys
        color: Box color (uses config default if None)
        thickness: Box thickness (uses config default if None)
        font_scale: Font scale (uses config default if None)
        font_thickness: Font thickness (uses config default if None)
        
    Returns:
        Image with all detections drawn
    """
    # Get config defaults
    config = get_config()
    viz_config = config.get('visualization', {})
    
    if color is None:
        color = tuple(viz_config.get('box_color', [0, 255, 0]))
    if thickness is None:
        thickness = viz_config.get('box_thickness', 2)
    if font_scale is None:
        font_scale = viz_config.get('font_scale', 0.6)
    if font_thickness is None:
        font_thickness = viz_config.get('font_thickness', 2)
    
    # Make a copy to avoid modifying original
    result = image.copy()
    
    # Draw each detection
    for detection in detections:
        bbox = detection.get('bbox')
        label = detection.get('label', '')
        
        if bbox:
            result = draw_bounding_box(
                result, bbox, label, color, thickness, font_scale, font_thickness
            )
    
    return result


def yolo_to_bbox(
    yolo_coords: Tuple[float, float, float, float],
    image_width: int,
    image_height: int
) -> Tuple[int, int, int, int]:
    """
    Convert YOLO format coordinates to bounding box format.
    
    Args:
        yolo_coords: (center_x, center_y, width, height) in normalized coordinates
        image_width: Image width in pixels
        image_height: Image height in pixels
        
    Returns:
        Bounding box (x, y, width, height) in pixels
    """
    center_x, center_y, width, height = yolo_coords
    
    # Convert from normalized to pixel coordinates
    x = int((center_x - width / 2) * image_width)
    y = int((center_y - height / 2) * image_height)
    w = int(width * image_width)
    h = int(height * image_height)
    
    return (x, y, w, h)


def bbox_to_yolo(
    bbox: Tuple[int, int, int, int],
    image_width: int,
    image_height: int
) -> Tuple[float, float, float, float]:
    """
    Convert bounding box format to YOLO format.
    
    Args:
        bbox: (x, y, width, height) in pixels
        image_width: Image width in pixels
        image_height: Image height in pixels
        
    Returns:
        YOLO coordinates (center_x, center_y, width, height) in normalized coordinates
    """
    x, y, w, h = bbox
    
    # Convert to normalized coordinates
    center_x = (x + w / 2) / image_width
    center_y = (y + h / 2) / image_height
    width = w / image_width
    height = h / image_height
    
    return (center_x, center_y, width, height)


def save_visualization(
    image: np.ndarray,
    output_path: str,
    quality: int = 95
) -> None:
    """
    Save an image to disk.
    
    Args:
        image: Image to save (BGR format)
        output_path: Path to save the image
        quality: JPEG quality (0-100)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Set compression parameters
    if output_path.suffix.lower() in ['.jpg', '.jpeg']:
        params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    elif output_path.suffix.lower() == '.png':
        params = [cv2.IMWRITE_PNG_COMPRESSION, 9]
    else:
        params = []
    
    cv2.imwrite(str(output_path), image, params)


def display_image(
    image: np.ndarray,
    window_name: str = "Image",
    wait_key: int = 0
) -> None:
    """
    Display an image in a window.
    
    Args:
        image: Image to display (BGR format)
        window_name: Name of the display window
        wait_key: Time to wait in milliseconds (0 = wait for key press)
    """
    cv2.imshow(window_name, image)
    cv2.waitKey(wait_key)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Test visualization functions
    test_image = np.zeros((500, 500, 3), dtype=np.uint8)
    
    detections = [
        {'bbox': (50, 50, 100, 100), 'label': 'QR Code'},
        {'bbox': (200, 200, 150, 80), 'label': 'Barcode'},
    ]
    
    result = draw_detections(test_image, detections)
    display_image(result, "Test Visualization", 2000)
    print("Visualization test complete!")
