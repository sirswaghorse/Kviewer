"""
Mini map panel for the KitelyView viewer using PyQt5.
Displays a top-down view of the current region.
"""

import logging
import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont, QPixmap

class MiniMapPanel(QWidget):
    """Panel for displaying a mini map of the region"""
    
    def __init__(self, parent):
        """Initialize the mini map panel"""
        super(MiniMapPanel, self).__init__(parent)
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.mini_map")
        self.logger.info("Initializing mini map panel")
        
        # Store parent reference (MainWindow)
        self.main_window = parent
        
        # Set minimum size
        self.setMinimumSize(200, 200)
        
        # Create main layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # Create map widget
        self.map_widget = MapWidget(self)
        self.layout.addWidget(self.map_widget)
        
        # Set up update timer (1 second)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_map)
        self.update_timer.start(1000)
        
        self.logger.info("Mini map panel initialized")
        
    def update_map(self):
        """Update map display"""
        if self.isVisible():
            self.map_widget.update()
            
    def on_login_success(self):
        """Handle successful login"""
        # Start updating the map
        if not self.update_timer.isActive():
            self.update_timer.start(1000)
            
    def on_logout(self):
        """Handle logout"""
        # Stop updating the map
        if self.update_timer.isActive():
            self.update_timer.stop()
        
        # Clear the map
        self.map_widget.clear()


class MapWidget(QWidget):
    """Widget for rendering the map"""
    
    def __init__(self, parent):
        """Initialize the map widget"""
        super(MapWidget, self).__init__(parent)
        
        # Store parent reference
        self.mini_map = parent
        
        # Set attributes
        self.setMinimumSize(200, 200)
        
        # Map state
        self.region_name = "Unknown Region"
        self.region_size = 256  # Standard OpenSim region size
        self.player_x = self.region_size / 2
        self.player_y = self.region_size / 2
        self.player_rotation = 0  # In degrees
        
        # Terrain data (simplified)
        self.terrain_heightmap = None
        
        # Avatar positions (other than player)
        self.avatars = []
        
        # Object positions
        self.objects = []
        
        # Map is initially clear
        self.is_clear = True
        
    def clear(self):
        """Clear the map data"""
        self.region_name = "Unknown Region"
        self.player_x = self.region_size / 2
        self.player_y = self.region_size / 2
        self.player_rotation = 0
        self.terrain_heightmap = None
        self.avatars = []
        self.objects = []
        self.is_clear = True
        self.update()
        
    def set_position(self, x, y, rotation=None):
        """Set player position on the map"""
        self.player_x = x
        self.player_y = y
        if rotation is not None:
            self.player_rotation = rotation
            
        # Mark the map as having data
        self.is_clear = False
        
        # Update display
        self.update()
        
    def add_avatar(self, x, y, name):
        """Add avatar to the map"""
        self.avatars.append((x, y, name))
        self.is_clear = False
        self.update()
        
    def add_object(self, x, y, name=None):
        """Add object to the map"""
        self.objects.append((x, y, name))
        self.is_clear = False
        self.update()
        
    def set_region(self, name, size=256):
        """Set region information"""
        self.region_name = name
        self.region_size = size
        self.is_clear = False
        self.update()
        
    def paintEvent(self, event):
        """Handle paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget size
        width = self.width()
        height = self.height()
        
        # Draw background
        painter.fillRect(0, 0, width, height, QColor(200, 230, 255))
        
        if self.is_clear:
            # Draw "No Map Data" message
            painter.setPen(Qt.black)
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(
                QRect(0, 0, width, height),
                Qt.AlignCenter,
                "No Map Data"
            )
            return
            
        # Calculate scale factor to fit region in widget
        scale = min(width, height) / self.region_size
        
        # Draw region border
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(
            0, 
            0, 
            self.region_size * scale, 
            self.region_size * scale
        )
        
        # Draw terrain heightmap (simplified as a gradient)
        if self.terrain_heightmap is None:
            # No real terrain data, just draw a gradient
            for y in range(0, int(self.region_size * scale), 4):
                for x in range(0, int(self.region_size * scale), 4):
                    # Calculate a simple height value based on position
                    rel_x = x / (self.region_size * scale)
                    rel_y = y / (self.region_size * scale)
                    height = math.sin(rel_x * 4) * math.cos(rel_y * 4) * 0.5 + 0.5
                    
                    # Set color based on height
                    if height < 0.3:  # Water
                        color = QColor(50, 100, 200)
                    elif height < 0.4:  # Beach
                        color = QColor(240, 240, 150)
                    elif height < 0.7:  # Land
                        color = QColor(30, 180, 30)
                    else:  # Mountains
                        color = QColor(150, 100, 70)
                        
                    painter.fillRect(
                        x, 
                        y, 
                        4, 
                        4, 
                        color
                    )
        
        # Draw objects
        painter.setPen(Qt.black)
        painter.setBrush(QBrush(QColor(150, 150, 150)))
        for x, y, name in self.objects:
            painter.drawRect(
                int(x * scale - 2),
                int(y * scale - 2),
                4,
                4
            )
        
        # Draw other avatars
        painter.setPen(Qt.black)
        painter.setBrush(QBrush(QColor(0, 200, 0)))
        for x, y, name in self.avatars:
            painter.drawEllipse(
                QPoint(int(x * scale), int(y * scale)),
                3,
                3
            )
            
            # Draw name if provided
            if name:
                painter.drawText(
                    int(x * scale + 5),
                    int(y * scale + 3),
                    name
                )
        
        # Draw player avatar
        painter.setPen(Qt.black)
        painter.setBrush(QBrush(QColor(200, 0, 0)))
        
        # Save current state
        painter.save()
        
        # Translate to player position and rotate
        painter.translate(int(self.player_x * scale), int(self.player_y * scale))
        painter.rotate(self.player_rotation)
        
        # Draw player arrow
        points = [
            QPoint(0, -5),    # Tip
            QPoint(-3, 3),    # Bottom left
            QPoint(0, 1),     # Bottom middle
            QPoint(3, 3)      # Bottom right
        ]
        painter.drawPolygon(points)
        
        # Restore painter state
        painter.restore()
        
        # Draw region name
        painter.setPen(Qt.black)
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(
            5,
            height - 5,
            f"Region: {self.region_name}"
        )
        
        # Draw coordinates
        painter.drawText(
            5,
            15,
            f"Pos: {int(self.player_x)}, {int(self.player_y)}"
        )