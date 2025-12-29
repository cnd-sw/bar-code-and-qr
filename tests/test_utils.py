"""
Test suite for utility modules.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import load_config, get_config_value, get_project_root
from src.utils.visualization import yolo_to_bbox, bbox_to_yolo


class TestConfig:
    """Test configuration utilities."""
    
    def test_get_project_root(self):
        """Test getting project root directory."""
        root = get_project_root()
        assert root.exists()
        assert (root / "config.yaml").exists()
    
    def test_load_config(self):
        """Test loading configuration file."""
        config = load_config()
        assert config is not None
        assert 'paths' in config
        assert 'qr_detection' in config
        assert 'barcode_detection' in config
    
    def test_get_config_value(self):
        """Test getting configuration values."""
        config = load_config()
        qr_path = get_config_value(config, 'paths.qr_data')
        assert qr_path == 'qr_data'
        
        # Test default value
        missing = get_config_value(config, 'nonexistent.key', 'default')
        assert missing == 'default'


class TestVisualization:
    """Test visualization utilities."""
    
    def test_yolo_to_bbox(self):
        """Test YOLO to bbox conversion."""
        yolo_coords = (0.5, 0.5, 0.4, 0.4)
        bbox = yolo_to_bbox(yolo_coords, 100, 100)
        assert bbox == (30, 30, 40, 40)
    
    def test_bbox_to_yolo(self):
        """Test bbox to YOLO conversion."""
        bbox = (30, 30, 40, 40)
        yolo_coords = bbox_to_yolo(bbox, 100, 100)
        assert yolo_coords == (0.5, 0.5, 0.4, 0.4)
    
    def test_round_trip_conversion(self):
        """Test round-trip conversion."""
        original_yolo = (0.5, 0.5, 0.4, 0.4)
        bbox = yolo_to_bbox(original_yolo, 100, 100)
        converted_yolo = bbox_to_yolo(bbox, 100, 100)
        
        # Check each component (with small tolerance for floating point)
        for orig, conv in zip(original_yolo, converted_yolo):
            assert abs(orig - conv) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
