"""
Configuration loader utility.

This module provides functions to load and access configuration settings.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path: Path to the project root directory
    """
    return Path(__file__).parent.parent.parent


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file. If None, uses default config.yaml
        
    Returns:
        Dictionary containing configuration settings
    """
    if config_path is None:
        config_path = get_project_root() / "config.yaml"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get a configuration value using dot notation.
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated path to the config value (e.g., 'paths.qr_data')
        default: Default value if key not found
        
    Returns:
        Configuration value or default
        
    Example:
        >>> config = load_config()
        >>> qr_path = get_config_value(config, 'paths.qr_data')
    """
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


def get_absolute_path(relative_path: str) -> Path:
    """
    Convert a relative path to an absolute path from project root.
    
    Args:
        relative_path: Relative path from project root
        
    Returns:
        Absolute Path object
    """
    return get_project_root() / relative_path


def ensure_dir_exists(path: Path) -> None:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        path: Path to directory
    """
    path.mkdir(parents=True, exist_ok=True)


# Global config instance
_config = None


def get_config() -> Dict[str, Any]:
    """
    Get the global configuration instance.
    Loads config on first call, then returns cached version.
    
    Returns:
        Configuration dictionary
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


if __name__ == "__main__":
    # Test configuration loading
    config = load_config()
    print("Configuration loaded successfully!")
    print(f"QR data path: {get_config_value(config, 'paths.qr_data')}")
    print(f"Barcode data path: {get_config_value(config, 'paths.barcode_data')}")
    print(f"Project root: {get_project_root()}")
