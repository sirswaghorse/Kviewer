"""
Main window for the KitelyView application.
Integrates all UI components and manages the application flow.
"""

import logging
import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QDesktopWidget, QDockWidget, 
    QStatusBar, QAction, QMenu, QToolBar, QMessageBox
)
from PyQt5.QtCore import Qt, QSize, QTimer, QSettings
from PyQt5.QtGui import QIcon, QFont, QPixmap

from app.config import Config
from app.ui.qt_login_panel import LoginPanel
from app.ui.qt_world_view import WorldViewPanel
from app.ui.qt_chat_panel import ChatPanel
from app.ui.qt_inventory_panel import InventoryPanel
from app.ui.qt_mini_map import MiniMapPanel
from app.ui.qt_toolbar import ViewerToolbar
from app.models.user import User

class MainWindow(QMainWindow):
    """Main window for the KitelyView application"""
    
    def __init__(self):
        """Initialize the main window"""
        super(MainWindow, self).__init__()
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.main_window")
        self.logger.info("Initializing main window")
        
        # Initialize config
        self.config = Config()
        
        # Set application state
        self.is_logged_in = False
        self.user = None
        
        # Set window properties
        self.setWindowTitle("KitelyView")
        self.resize(1024, 768)
        self.center_on_screen()
        
        # Set application icon
        self.setWindowIcon(QIcon("app/assets/icons/app_icon.svg"))
        
        # Initialize UI components
        self._create_ui()
        
        # Show welcome message
        self.update_status("Welcome to KitelyView", 0)
        
        self.logger.info("Main window initialized")
        
    def _create_ui(self):
        """Create the UI components"""
        # Create central widget (3D view)
        self.world_view = WorldViewPanel(self)
        self.setCentralWidget(self.world_view)
        
        # Create status bar
        self.status_bar = self.statusBar()
        self.status_message = QStatusBar.insertPermanentWidget(self.status_bar, 0)
        self.region_info = QStatusBar.insertPermanentWidget(self.status_bar, 1)
        self.fps_display = QStatusBar.insertPermanentWidget(self.status_bar, 2)
        
        # Create login panel
        self.login_dock = QDockWidget("Login", self)
        self.login_dock.setAllowedAreas(Qt.NoDockWidgetArea)
        self.login_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.login_panel = LoginPanel(self)
        self.login_dock.setWidget(self.login_panel)
        
        # Create chat panel
        self.chat_dock = QDockWidget("Chat", self)
        self.chat_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.chat_panel = ChatPanel(self)
        self.chat_dock.setWidget(self.chat_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.chat_dock)
        self.chat_dock.hide()  # Initially hidden until login
        
        # Create inventory panel
        self.inventory_dock = QDockWidget("Inventory", self)
        self.inventory_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.inventory_panel = InventoryPanel(self)
        self.inventory_dock.setWidget(self.inventory_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.inventory_dock)
        self.inventory_dock.hide()  # Initially hidden until login
        
        # Create mini map panel
        self.mini_map_dock = QDockWidget("Mini Map", self)
        self.mini_map_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.mini_map_panel = MiniMapPanel(self)
        self.mini_map_dock.setWidget(self.mini_map_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.mini_map_dock)
        self.mini_map_dock.hide()  # Initially hidden until login
        
        # Create toolbar
        self.toolbar = ViewerToolbar(self)
        self.addToolBar(self.toolbar)
        self.toolbar.hide()  # Initially hidden until login
        
        # Create menus
        self._create_menus()
        
        # Show login panel
        self.login_dock.setFloating(True)
        self.login_dock.show()
        
    def _create_menus(self):
        """Create application menus"""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        login_action = QAction("&Login", self)
        login_action.setStatusTip("Log in to the grid")
        login_action.triggered.connect(self.show_login_panel)
        file_menu.addAction(login_action)
        
        logout_action = QAction("Log&out", self)
        logout_action.setStatusTip("Log out from the grid")
        logout_action.triggered.connect(self.logout)
        logout_action.setEnabled(False)
        self.logout_action = logout_action
        file_menu.addAction(logout_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("&View")
        
        chat_action = QAction("&Chat", self)
        chat_action.setStatusTip("Show/hide chat panel")
        chat_action.setCheckable(True)
        chat_action.setChecked(False)
        chat_action.triggered.connect(self.toggle_chat_panel)
        self.chat_action = chat_action
        view_menu.addAction(chat_action)
        
        inventory_action = QAction("&Inventory", self)
        inventory_action.setStatusTip("Show/hide inventory panel")
        inventory_action.setCheckable(True)
        inventory_action.setChecked(False)
        inventory_action.triggered.connect(self.toggle_inventory_panel)
        self.inventory_action = inventory_action
        view_menu.addAction(inventory_action)
        
        map_action = QAction("&Map", self)
        map_action.setStatusTip("Show/hide mini map")
        map_action.setCheckable(True)
        map_action.setChecked(False)
        map_action.triggered.connect(self.toggle_mini_map)
        self.map_action = map_action
        view_menu.addAction(map_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QAction("&Fullscreen", self)
        fullscreen_action.setStatusTip("Toggle fullscreen mode")
        fullscreen_action.setCheckable(True)
        fullscreen_action.setChecked(False)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.setStatusTip("About KitelyView")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def center_on_screen(self):
        """Center the window on the screen"""
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
        
    def login_success(self, user_data):
        """Handle successful login"""
        self.logger.info(f"Login successful for user: {user_data['name']}")
        
        # Set logged in state
        self.is_logged_in = True
        
        # Create user object
        self.user = User(user_data['id'], user_data['name'])
        
        # Update window title
        self.setWindowTitle(f"KitelyView - {user_data['name']}")
        
        # Hide login panel
        self.login_dock.hide()
        
        # Update UI
        self.logout_action.setEnabled(True)
        self.toolbar.show()
        
        # Show panels
        self.chat_dock.show()
        self.inventory_dock.show()
        self.mini_map_dock.show()
        self.chat_action.setChecked(True)
        self.inventory_action.setChecked(True)
        self.map_action.setChecked(True)
        
        # Notify components
        self.world_view.on_login_success()
        self.chat_panel.on_login_success()
        self.inventory_panel.on_login_success()
        self.mini_map_panel.on_login_success()
        
        # Update status bar
        self.update_status(f"Logged in as {user_data['name']}", 0)
        self.update_status(f"Region: {user_data['current_region']}", 1)
        
    def logout(self):
        """Log out from the grid"""
        if not self.is_logged_in:
            return
            
        self.logger.info("Logging out")
        
        # Reset state
        self.is_logged_in = False
        self.user = None
        
        # Reset window title
        self.setWindowTitle("KitelyView")
        
        # Update UI
        self.logout_action.setEnabled(False)
        self.toolbar.hide()
        
        # Hide panels
        self.chat_dock.hide()
        self.inventory_dock.hide()
        self.mini_map_dock.hide()
        self.chat_action.setChecked(False)
        self.inventory_action.setChecked(False)
        self.map_action.setChecked(False)
        
        # Notify components
        self.world_view.on_logout()
        self.chat_panel.on_logout()
        self.inventory_panel.on_logout()
        self.mini_map_panel.on_logout()
        
        # Show login panel
        self.login_dock.show()
        
        # Update status bar
        self.update_status("Logged out", 0)
        self.update_status("", 1)
        
    def show_login_panel(self):
        """Show the login panel"""
        self.login_dock.show()
        
    def toggle_chat_panel(self, checked):
        """Toggle chat panel visibility"""
        self.chat_dock.setVisible(checked)
        
    def toggle_inventory_panel(self, checked):
        """Toggle inventory panel visibility"""
        self.inventory_dock.setVisible(checked)
        
    def toggle_mini_map(self, checked):
        """Toggle mini map visibility"""
        self.mini_map_dock.setVisible(checked)
        
    def toggle_fullscreen(self, checked):
        """Toggle fullscreen mode"""
        if checked:
            self.setWindowState(self.windowState() | Qt.WindowFullScreen)
        else:
            self.setWindowState(self.windowState() & ~Qt.WindowFullScreen)
            
    def update_status(self, message, position=0):
        """Update status bar message"""
        if position == 0:
            self.statusBar().showMessage(message)
        elif position == 1:
            self.region_info.setText(message)
        elif position == 2:
            self.fps_display.setText(message)
            
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, 
            "About KitelyView",
            "<h3>KitelyView</h3>"
            "<p>Version 0.1</p>"
            "<p>A cross-platform OpenSimulator viewer for connecting to the Kitely grid.</p>"
            "<p>Developed for educational purposes.</p>"
        )
        
    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_logged_in:
            # Ask if the user wants to log out
            reply = QMessageBox.question(
                self, 
                "Confirm Exit",
                "You are still logged in. Do you want to exit?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Log out and accept the close event
                self.logout()
                event.accept()
            else:
                # Reject the close event
                event.ignore()
        else:
            # Not logged in, just close
            event.accept()