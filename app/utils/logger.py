"""
Logging setup for the KitelyView application.
"""

import os
import logging
import sys
from datetime import datetime

def setup_logger():
    """Set up logging for the application"""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    # Add file handler with date in filename
    log_file = os.path.join(
        log_dir, 
        f'kitelyview_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    )
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # Create application-specific logger
    app_logger = logging.getLogger('kitelyview')
    
    return app_logger