#!/usr/bin/env python3
"""
KitelyView - A cross-platform OpenSimulator viewer for connecting to the Kitely grid.
This application supports Windows, Fedora, and Ubuntu platforms.
"""

import os
import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from app.config import Config
from app.utils.logger import setup_logger

def main():
    """Main entry point for the application"""
    # Setup logging
    setup_logger()
    logger = logging.getLogger("kitelyview")
    
    # Log platform info
    logger.info(f"Starting KitelyView on {sys.platform}")
    
    # Initialize configuration
    config = Config()
    
    # Create and start the Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("KitelyView")
    
    # Import here to avoid circular imports
    from app.ui.qt_main_window import MainWindow
    
    # Create main window
    main_window = MainWindow(config)
    main_window.show()
    
    # Run application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
