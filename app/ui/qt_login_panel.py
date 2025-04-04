"""
Login panel for the KitelyView viewer using PyQt5.
Handles user authentication to the Kitely grid.
"""

import logging
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QComboBox, QProgressBar, QDesktopWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
from app.network.connection import GridConnection

class LoginWorker(QThread):
    """Worker thread for login operations"""
    # Define signals
    finished = pyqtSignal(bool, object)
    progress = pyqtSignal(int, str)
    
    def __init__(self, connection, first_name, last_name, password, location):
        """Initialize login worker thread"""
        super(LoginWorker, self).__init__()
        self.connection = connection
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.location = location
        
    def run(self):
        """Run the login process"""
        try:
            # Update progress
            self.progress.emit(30, "Authenticating...")
            
            # Attempt login
            success, result = self.connection.login(
                self.first_name, 
                self.last_name, 
                self.password, 
                self.location
            )
            
            if success:
                # Update progress
                self.progress.emit(70, "Loading world...")
            
            # Emit finished signal with result
            self.finished.emit(success, result)
            
        except Exception as e:
            # Handle unexpected errors
            self.finished.emit(False, f"Error during login: {str(e)}")

class LoginPanel(QWidget):
    """Panel for handling login to the Kitely grid"""
    
    def __init__(self, parent):
        """Initialize the login panel"""
        super(LoginPanel, self).__init__(parent)
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.login_panel")
        self.logger.info("Initializing login panel")
        
        # Store parent reference (MainWindow)
        self.main_window = parent
        
        # Create grid connection
        self.connection = GridConnection(self.main_window.config)
        
        # Set up panel style 
        pal = self.palette()
        pal.setColor(QPalette.Background, QColor(240, 240, 240))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        
        # Set fixed size
        self.setMinimumSize(400, 350)
        self.setMaximumSize(450, 400)
        
        # Create UI elements
        self._create_ui()
        
        # Load grid info
        self._load_grid_info()
        
        self.logger.info("Login panel initialized")
        
    def _create_ui(self):
        """Create UI elements"""
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add logo/banner
        logo_label = QLabel("KitelyView")
        logo_font = QFont()
        logo_font.setPointSize(24)
        logo_font.setBold(True)
        logo_label.setFont(logo_font)
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)
        
        # Add grid selector
        grid_layout = QHBoxLayout()
        grid_label = QLabel("Grid:")
        self.grid_choice = QComboBox()
        self.grid_choice.addItem("Kitely")
        grid_layout.addWidget(grid_label)
        grid_layout.addWidget(self.grid_choice)
        main_layout.addLayout(grid_layout)
        
        # Username field
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_ctrl = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_ctrl)
        main_layout.addLayout(username_layout)
        
        # Password field
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_ctrl = QLineEdit()
        self.password_ctrl.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_ctrl)
        main_layout.addLayout(password_layout)
        
        # Location field
        location_layout = QHBoxLayout()
        location_label = QLabel("Location:")
        self.location_ctrl = QLineEdit("last")
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_ctrl)
        main_layout.addLayout(location_layout)
        
        # Remember password checkbox
        self.remember_checkbox = QCheckBox("Remember password")
        main_layout.addWidget(self.remember_checkbox)
        
        # Status message
        self.status_text = QLabel("")
        pal = self.status_text.palette()
        pal.setColor(QPalette.WindowText, QColor(200, 0, 0))
        self.status_text.setPalette(pal)
        main_layout.addWidget(self.status_text)
        
        # Progress indicator
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.cancel_button = QPushButton("Cancel")
        
        self.login_button.setDefault(True)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)
        
        # Add register and help links
        link_layout = QHBoxLayout()
        register_link = QLabel('<a href="https://www.kitely.com/register">Register Account</a>')
        register_link.setOpenExternalLinks(True)
        help_link = QLabel('<a href="https://www.kitely.com/virtual-world-help">Need Help?</a>')
        help_link.setOpenExternalLinks(True)
        
        link_layout.addWidget(register_link)
        link_layout.addStretch()
        link_layout.addWidget(help_link)
        main_layout.addLayout(link_layout)
        
        # Set main layout
        self.setLayout(main_layout)
        
        # Connect signals
        self.login_button.clicked.connect(self.on_login)
        self.cancel_button.clicked.connect(self.on_cancel)
        self.grid_choice.currentIndexChanged.connect(self.on_grid_change)
        
    def _load_grid_info(self):
        """Load grid information"""
        # Set default grid to Kitely
        self.grid_choice.setCurrentIndex(0)
        
        # In the future, could load from a configuration file with multiple grids
        
    def on_grid_change(self, index):
        """Handle grid selection change"""
        # Currently only Kitely is supported
        pass
        
    def on_login(self):
        """Handle login button press"""
        # Get login credentials
        username = self.username_ctrl.text().strip()
        password = self.password_ctrl.text().strip()
        location = self.location_ctrl.text().strip()
        
        # Validate input
        if not username:
            self.show_error("Please enter a username")
            return
            
        if not password:
            self.show_error("Please enter a password")
            return
            
        # Parse username into first/last name if needed
        user_parts = username.split(' ')
        if len(user_parts) == 1:
            # Assume the format is first.last
            name_parts = username.split('.')
            if len(name_parts) == 2:
                first_name = name_parts[0]
                last_name = name_parts[1]
            else:
                self.show_error("Invalid username format. Use 'First Last' or 'First.Last'")
                return
        else:
            first_name = user_parts[0]
            last_name = ' '.join(user_parts[1:])
            
        # Show progress indicator
        self.progress.setVisible(True)
        self.progress.setValue(10)
        self.login_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.status_text.setText("Connecting to grid...")
        
        # Create and start worker thread
        self.login_worker = LoginWorker(
            self.connection, 
            first_name, 
            last_name, 
            password, 
            location
        )
        
        # Connect signals
        self.login_worker.progress.connect(self.update_progress)
        self.login_worker.finished.connect(self.login_finished)
        
        # Start thread
        self.login_worker.start()
    
    def update_progress(self, value, message):
        """Update progress bar and status message"""
        self.progress.setValue(value)
        self.status_text.setText(message)
    
    def login_finished(self, success, result):
        """Handle login completion"""
        if success:
            # Update progress
            self.progress.setValue(100)
            
            # Save username (not password) for next time
            # TODO: Implement config saving
            
            # Notify the main window
            self.main_window.login_success(result)
            
            # Reset UI
            self.progress.setVisible(False)
            self.login_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
            self.status_text.setText("")
            
            # If not remembering password, clear it
            if not self.remember_checkbox.isChecked():
                self.password_ctrl.clear()
        else:
            # Handle login failure
            self.show_error(f"Login failed: {result}")
            self.progress.setVisible(False)
            self.login_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
    
    def on_cancel(self):
        """Handle cancel button press"""
        # Hide the login panel
        self.main_window.login_dock.hide()
        
        # Clear any error message
        self.status_text.setText("")
        
        # If login is in progress, cancel it
        if not self.login_button.isEnabled() and hasattr(self, 'login_worker'):
            # Attempt to terminate the worker thread
            self.login_worker.terminate()
            self.login_worker.wait()
            
            self.login_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
            self.progress.setVisible(False)
    
    def show_error(self, message):
        """Display an error message"""
        self.status_text.setText(message)