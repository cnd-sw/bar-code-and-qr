"""
Logging utility module.

Provides consistent logging across the application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from src.utils.config import get_config, get_project_root, ensure_dir_exists


def setup_logger(
    name: str = "qr_barcode_detector",
    level: str = None,
    log_file: str = None,
    console: bool = True
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses config setting
        console: Whether to also log to console
        
    Returns:
        Configured logger instance
    """
    # Get config
    config = get_config()
    
    # Set level from config if not provided
    if level is None:
        level = config.get('logging', {}).get('level', 'INFO')
    
    # Set log file from config if not provided
    if log_file is None and config.get('logging', {}).get('save_logs', True):
        log_file = config.get('logging', {}).get('log_file', 'outputs/app.log')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add file handler if log_file is specified
    if log_file:
        log_path = get_project_root() / log_file
        ensure_dir_exists(log_path.parent)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "qr_barcode_detector") -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up
    if not logger.handlers:
        logger = setup_logger(name)
    
    return logger


if __name__ == "__main__":
    # Test logger
    logger = setup_logger()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
