#!/usr/bin/env python3
"""
KitelyView - A cross-platform OpenSimulator viewer for connecting to the Kitely grid.
This application supports Windows, Fedora, and Ubuntu platforms.
"""

import sys
import os
import logging
import traceback
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Set platform to offscreen for headless environments like Replit
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from app.ui.qt_main_window import MainWindow
from app.utils.logger import setup_logger

def excepthook(exc_type, exc_value, exc_traceback):
    """
    Global exception handler to log uncaught exceptions
    """
    logger = logging.getLogger("kitelyview")
    logger.error("Uncaught exception", 
                exc_info=(exc_type, exc_value, exc_traceback))
    # Also print to stderr
    traceback.print_exception(exc_type, exc_value, exc_traceback)

def main():
    """Main entry point for the application"""
    # Set up logging
    logger = setup_logger()
    
    # Set global exception handler
    sys.excepthook = excepthook
    
    logger.info("Starting KitelyView")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("KitelyView")
    app.setOrganizationName("KitelyView")
    app.setOrganizationDomain("kitelyview.org")
    
    # Enable high DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create main window
    window = MainWindow()
    
    # Just logging information since we're in offscreen mode for Replit
    logger.info("Main window created. Note: Running in offscreen mode for Replit")
    logger.info("In real usage on Windows/Linux/Mac, the UI would be visible")
    
    # Take a screenshot of the window to demonstrate it was created
    if hasattr(window, 'grab'):
        pixmap = window.grab()
        pixmap.save("kitelyview_screenshot.png")
        logger.info("Screenshot saved to kitelyview_screenshot.png")
    
    # Run the application
    logger.info("Application started, entering main event loop")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()