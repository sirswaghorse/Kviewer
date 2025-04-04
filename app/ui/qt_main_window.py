"""
Main window for the KitelyView application using PyQt5.
Integrates all UI components and manages the application layout.
"""

import logging
import os
from PyQt5.QtWidgets import (
    QMainWindow, QDockWidget, QAction, QMenu, QMenuBar, 
    QStatusBar, QToolBar, QMessageBox, QDesktopWidget
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from app.network.connection import GridConnection
from app.models.user import User
from app.renderer.scene import Scene
from app.ui.qt_login_panel import LoginPanel
from app.ui.qt_world_view import WorldViewPanel
from app.ui.qt_chat_panel import ChatPanel
from app.ui.qt_inventory_panel import InventoryPanel
from app.ui.qt_mini_map import MiniMapPanel
from app.ui.qt_toolbar import ViewerToolbar

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config):
        """Initialize the main window"""
        # Get window size from config
        resolution = config.get("viewer", "resolution")
        
        # Call parent constructor
        super(MainWindow, self).__init__()
        
        # Set window title and size
        self.setWindowTitle("KitelyView - OpenSimulator Viewer")
        self.resize(resolution[0], resolution[1])
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.main_window")
        self.logger.info("Initializing main window")
        
        # Store configuration
        self.config = config
        
        # Set application icon
        self._set_application_icon()
        
        # Initialize class variables
        self.is_logged_in = False
        self.user = User()
        self.connection = GridConnection(config)
        self.scene = Scene(self)
        
        # Create UI components
        self._create_menu_bar()
        self._create_status_bar()
        self._create_panels()
        
        # Center on screen
        self._center_on_screen()
        
        # Set up fullscreen if configured
        if config.get("viewer", "fullscreen"):
            self.showFullScreen()
            
        self.logger.info("Main window initialized")
        
    def _set_application_icon(self):
        """Set the application icon"""
        try:
            # TODO: Replace with actual icon loading when available
            pass
        except Exception as e:
            self.logger.error(f"Failed to set application icon: {e}")
    
    def _create_menu_bar(self):
        """Create the application menu bar"""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        self.login_action = QAction("&Login", self)
        self.login_action.setShortcut("Ctrl+L")
        self.login_action.setStatusTip("Login to Kitely grid")
        self.login_action.triggered.connect(self.on_login)
        file_menu.addAction(self.login_action)
        
        self.logout_action = QAction("Log&out", self)
        self.logout_action.setShortcut("Ctrl+O")
        self.logout_action.setStatusTip("Logout from grid")
        self.logout_action.triggered.connect(self.on_logout)
        file_menu.addAction(self.logout_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.on_exit)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        
        preferences_action = QAction("&Preferences", self)
        preferences_action.setShortcut("Ctrl+P")
        preferences_action.setStatusTip("Edit preferences")
        preferences_action.triggered.connect(self.on_preferences)
        edit_menu.addAction(preferences_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("&View")
        
        fullscreen_action = QAction("&Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.setStatusTip("Toggle fullscreen mode")
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self.on_toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        view_menu.addSeparator()
        
        reset_layout_action = QAction("&Reset Layout", self)
        reset_layout_action.setStatusTip("Reset the window layout")
        reset_layout_action.triggered.connect(self.on_reset_layout)
        view_menu.addAction(reset_layout_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.setShortcut("F1")
        about_action.setStatusTip("About KitelyView")
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        
    def _create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Create permanent widgets for status sections
        self.main_status_label = QStatusBar()
        self.connection_status_label = QStatusBar()
        self.fps_status_label = QStatusBar()
        
        # Add widgets to status bar
        self.status_bar.addWidget(self.main_status_label, 3)
        self.status_bar.addPermanentWidget(self.connection_status_label, 1)
        self.status_bar.addPermanentWidget(self.fps_status_label, 1)
        
        # Set initial status
        self.update_status("Ready")
        
    def _create_panels(self):
        """Create and arrange UI panels"""
        # Create the toolbar
        self.toolbar = ViewerToolbar(self)
        self.addToolBar(self.toolbar)
        
        # Create central widget (World View)
        self.world_view = WorldViewPanel(self)
        self.setCentralWidget(self.world_view)
        
        # Create login panel as a floating widget
        self.login_panel = LoginPanel(self)
        self.login_dock = QDockWidget("Login", self)
        self.login_dock.setWidget(self.login_panel)
        self.login_dock.setFloating(True)
        self.login_dock.setAllowedAreas(Qt.NoDockWidgetArea)
        self.login_dock.setFeatures(QDockWidget.DockWidgetClosable)
        
        # Create chat panel
        self.chat_panel = ChatPanel(self)
        self.chat_dock = QDockWidget("Chat", self)
        self.chat_dock.setWidget(self.chat_panel)
        self.chat_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.chat_dock)
        
        # Create inventory panel
        self.inventory_panel = InventoryPanel(self)
        self.inventory_dock = QDockWidget("Inventory", self)
        self.inventory_dock.setWidget(self.inventory_panel)
        self.inventory_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.inventory_dock)
        
        # Create mini map panel
        self.mini_map = MiniMapPanel(self)
        self.mini_map_dock = QDockWidget("Mini Map", self)
        self.mini_map_dock.setWidget(self.mini_map)
        self.mini_map_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.mini_map_dock)
        
        # Hide panels that should only be visible when logged in
        self.chat_dock.setVisible(self.is_logged_in)
        self.inventory_dock.setVisible(self.is_logged_in)
        self.mini_map_dock.setVisible(self.is_logged_in)
        
    def _center_on_screen(self):
        """Center the window on the screen"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
    def update_status(self, text, position=0):
        """Update the status bar text"""
        if position == 0:
            self.main_status_label.showMessage(text)
        elif position == 1:
            self.connection_status_label.showMessage(text)
        elif position == 2:
            self.fps_status_label.showMessage(text)
            
    def on_login(self):
        """Handle login menu click"""
        if not self.is_logged_in:
            if not self.login_dock.isVisible():
                self.login_dock.show()
                # Center the login panel over the main window
                main_geo = self.geometry()
                login_geo = self.login_dock.geometry()
                x = main_geo.x() + (main_geo.width() - login_geo.width()) // 2
                y = main_geo.y() + (main_geo.height() - login_geo.height()) // 2
                self.login_dock.move(x, y)
    
    def login_success(self, user_data):
        """Handle successful login"""
        self.is_logged_in = True
        self.user = User(user_data)
        
        # Update UI
        self.login_dock.hide()
        self.chat_dock.setVisible(True)
        self.inventory_dock.setVisible(True)
        self.mini_map_dock.setVisible(True)
        
        # Update status
        self.update_status(f"Logged in as {self.user.get_full_name()}")
        
        # Notify components
        self.world_view.on_login_success()
        self.chat_panel.on_login_success()
        self.inventory_panel.on_login_success()
        self.mini_map.on_login_success()
        
        self.logger.info(f"User logged in: {self.user.get_full_name()}")
    
    def on_logout(self):
        """Handle logout request"""
        if self.is_logged_in:
            reply = QMessageBox.question(
                self, 
                "Confirm Logout", 
                "Are you sure you want to log out?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.logout()
    
    def logout(self):
        """Perform logout"""
        if self.is_logged_in:
            # Disconnect from grid
            self.connection.disconnect()
            
            # Reset user
            self.is_logged_in = False
            self.user = User()
            
            # Update UI
            self.login_dock.show()
            self.chat_dock.setVisible(False)
            self.inventory_dock.setVisible(False)
            self.mini_map_dock.setVisible(False)
            
            # Update status
            self.update_status("Logged out")
            
            # Notify components
            self.world_view.on_logout()
            self.chat_panel.on_logout()
            self.inventory_panel.on_logout()
            self.mini_map.on_logout()
            
            self.logger.info("User logged out")
    
    def on_exit(self):
        """Handle exit request"""
        self.close()
    
    def on_preferences(self):
        """Show preferences dialog"""
        # To be implemented
        QMessageBox.information(
            self, 
            "Information", 
            "Preferences dialog not yet implemented"
        )
    
    def on_toggle_fullscreen(self, checked):
        """Toggle fullscreen mode"""
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()
    
    def on_reset_layout(self):
        """Reset the window layout to default"""
        # Save current state to detect what's visible
        is_logged_in = self.is_logged_in
        
        # Remove all dock widgets
        self.removeDockWidget(self.chat_dock)
        self.removeDockWidget(self.inventory_dock)
        self.removeDockWidget(self.mini_map_dock)
        
        # Re-add them with default configuration
        self.addDockWidget(Qt.BottomDockWidgetArea, self.chat_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.inventory_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.mini_map_dock)
        
        # Set visibility based on login state
        self.chat_dock.setVisible(is_logged_in)
        self.inventory_dock.setVisible(is_logged_in)
        self.mini_map_dock.setVisible(is_logged_in)
        
        self.logger.info("Layout reset to default")
    
    def on_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About KitelyView",
            """<b>KitelyView</b> v0.1.0
            <p>A cross-platform OpenSimulator viewer for connecting to the Kitely grid.</p>
            <p>Copyright &copy; 2023</p>
            <p><a href="https://www.kitely.com">www.kitely.com</a></p>
            <p>Developed by the KitelyView Development Team</p>
            <p>Licensed under MIT License</p>"""
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_logged_in:
            reply = QMessageBox.question(
                self, 
                "Confirm Exit", 
                "You are still logged in. Log out and close the application?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.connection.disconnect()
                self.destroy_app()
            else:
                event.ignore()  # Prevent closing
        else:
            self.destroy_app()
    
    def destroy_app(self):
        """Clean up and destroy the application"""
        self.logger.info("Shutting down application")
        
        # Save configuration
        self.config.save_config()