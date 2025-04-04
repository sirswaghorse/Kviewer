"""
Logging setup for KitelyView.
Handles log file creation and configuration.
"""

import os
import logging
import datetime
from logging.handlers import RotatingFileHandler

def setup_logger():
    """
    Set up application logging
    Returns the configured logger
    """
    # Create logger
    logger = logging.getLogger("kitelyview")
    logger.setLevel(logging.DEBUG)
    
    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Create log file handler
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"kitelyview_{timestamp}.log")
    
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging to file: {log_file}")
    
    return logger