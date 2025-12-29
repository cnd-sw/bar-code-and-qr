"""
File I/O utilities for reading images and annotations.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import json
import csv


def read_image(image_path: str) -> Optional[np.ndarray]:
    """
    Read an image from disk.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Image as numpy array (BGR format) or None if failed
    """
    image_path = Path(image_path)
    
    if not image_path.exists():
        return None
    
    image = cv2.imread(str(image_path))
    return image


def read_yolo_annotation(annotation_path: str) -> List[Tuple[int, float, float, float, float]]:
    """
    Read YOLO format annotation file.
    
    Args:
        annotation_path: Path to the .txt annotation file
        
    Returns:
        List of tuples (class_id, center_x, center_y, width, height)
    """
    annotation_path = Path(annotation_path)
    
    if not annotation_path.exists():
        return []
    
    annotations = []
    with open(annotation_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    center_x = float(parts[1])
                    center_y = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])
                    annotations.append((class_id, center_x, center_y, width, height))
    
    return annotations


def get_image_files(directory: str, extensions: List[str] = None) -> List[Path]:
    """
    Get all image files in a directory.
    
    Args:
        directory: Directory to search
        extensions: List of file extensions to include (e.g., ['.png', '.jpg'])
        
    Returns:
        List of image file paths
    """
    if extensions is None:
        extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
    
    directory = Path(directory)
    
    if not directory.exists():
        return []
    
    image_files = []
    for ext in extensions:
        image_files.extend(directory.rglob(f'*{ext}'))
        image_files.extend(directory.rglob(f'*{ext.upper()}'))
    
    return sorted(image_files)


def get_image_annotation_pairs(directory: str) -> List[Tuple[Path, Path]]:
    """
    Get pairs of image files and their corresponding annotation files.
    
    Args:
        directory: Directory containing images and annotations
        
    Returns:
        List of tuples (image_path, annotation_path)
    """
    directory = Path(directory)
    image_files = get_image_files(directory)
    
    pairs = []
    for image_path in image_files:
        annotation_path = image_path.with_suffix('.txt')
        if annotation_path.exists():
            pairs.append((image_path, annotation_path))
    
    return pairs


def save_results_csv(results: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save detection results to CSV file.
    
    Args:
        results: List of result dictionaries
        output_path: Path to output CSV file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not results:
        return
    
    # Get all unique keys from results
    fieldnames = set()
    for result in results:
        fieldnames.update(result.keys())
    fieldnames = sorted(fieldnames)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def save_results_json(results: List[Dict[str, Any]], output_path: str, indent: int = 2) -> None:
    """
    Save detection results to JSON file.
    
    Args:
        results: List of result dictionaries
        output_path: Path to output JSON file
        indent: JSON indentation level
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=indent)


def load_results_json(input_path: str) -> List[Dict[str, Any]]:
    """
    Load detection results from JSON file.
    
    Args:
        input_path: Path to input JSON file
        
    Returns:
        List of result dictionaries
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        return []
    
    with open(input_path, 'r') as f:
        results = json.load(f)
    
    return results


def get_image_dimensions(image_path: str) -> Optional[Tuple[int, int]]:
    """
    Get image dimensions without loading the entire image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (width, height) or None if failed
    """
    image = read_image(image_path)
    if image is None:
        return None
    
    height, width = image.shape[:2]
    return (width, height)


def create_output_filename(
    input_path: str,
    output_dir: str,
    suffix: str = "_detected",
    extension: str = None
) -> Path:
    """
    Create an output filename based on input filename.
    
    Args:
        input_path: Input file path
        output_dir: Output directory
        suffix: Suffix to add to filename
        extension: New extension (keeps original if None)
        
    Returns:
        Output file path
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    stem = input_path.stem
    ext = extension if extension else input_path.suffix
    
    output_filename = f"{stem}{suffix}{ext}"
    return output_dir / output_filename


if __name__ == "__main__":
    # Test file I/O functions
    from src.utils.config import get_project_root
    
    project_root = get_project_root()
    qr_dir = project_root / "qr_data"
    barcode_dir = project_root / "barcode_data" / "0"
    
    # Test getting image files
    qr_images = get_image_files(qr_dir)
    print(f"Found {len(qr_images)} QR code images")
    
    # Test getting image-annotation pairs
    barcode_pairs = get_image_annotation_pairs(barcode_dir)
    print(f"Found {len(barcode_pairs)} barcode image-annotation pairs")
    
    if barcode_pairs:
        # Test reading annotation
        img_path, ann_path = barcode_pairs[0]
        annotations = read_yolo_annotation(ann_path)
        print(f"Sample annotation: {annotations}")
