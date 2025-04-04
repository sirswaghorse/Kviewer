"""
Chat panel for the KitelyView viewer using PyQt5.
Handles in-world chat and messaging.
"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLineEdit, QPushButton, QComboBox, QLabel
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QTextCursor

class ChatPanel(QWidget):
    """Panel for handling in-world chat"""
    
    def __init__(self, parent):
        """Initialize the chat panel"""
        super(ChatPanel, self).__init__(parent)
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.chat_panel")
        self.logger.info("Initializing chat panel")
        
        # Store parent reference (MainWindow)
        self.main_window = parent
        
        # Create UI elements
        self._create_ui()
        
        self.logger.info("Chat panel initialized")
        
    def _create_ui(self):
        """Create UI elements"""
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create chat text display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setLineWrapMode(QTextEdit.WidgetWidth)
        
        # Create channel selector
        channel_layout = QHBoxLayout()
        channel_label = QLabel("Channel:")
        self.channel_selector = QComboBox()
        self.channel_selector.addItems(["Local", "Region", "Group", "IM"])
        channel_layout.addWidget(channel_label)
        channel_layout.addWidget(self.channel_selector)
        channel_layout.addStretch()
        
        # Create input area
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a message...")
        self.send_button = QPushButton("Send")
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.send_button)
        
        # Add all widgets to main layout
        main_layout.addWidget(self.chat_display)
        main_layout.addLayout(channel_layout)
        main_layout.addLayout(input_layout)
        
        # Set main layout
        self.setLayout(main_layout)
        
        # Connect signals
        self.send_button.clicked.connect(self.on_send_message)
        self.chat_input.returnPressed.connect(self.on_send_message)
        
    def on_send_message(self):
        """Handle send message button/enter key"""
        text = self.chat_input.text().strip()
        if text:
            # Get selected channel
            channel = self.channel_selector.currentText()
            
            # Log message
            self.logger.info(f"Chat message: ({channel}) {text}")
            
            # Add message to display (in real app would be sent to server)
            sender = self.main_window.user.get_full_name() if self.main_window.is_logged_in else "You"
            self.add_chat_message(sender, text, channel)
            
            # Clear input
            self.chat_input.clear()
    
    def add_chat_message(self, sender, text, channel="Local"):
        """Add a chat message to the display"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Format based on channel
        format_html = f"<b>[{channel}]</b> <span style='color: blue;'>{sender}:</span> {text}"
        
        # Add to display
        cursor.insertHtml(format_html + "<br>")
        
        # Scroll to bottom
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()
        
    def on_login_success(self):
        """Handle successful login"""
        self.add_chat_message("System", "Welcome to Kitely! You are now connected.", "System")
        
    def on_logout(self):
        """Handle logout"""
        self.chat_display.clear()
        self.chat_input.clear()