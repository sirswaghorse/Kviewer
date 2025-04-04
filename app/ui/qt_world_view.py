"""
World view panel for rendering the 3D OpenSimulator world using PyQt5.
"""

import logging
import time
import math
import numpy as np
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLU import *

from app.renderer.camera import Camera
from app.renderer.scene import Scene
from app.utils.vector import Vector3
from app.utils.matrix import Matrix4

class WorldViewPanel(QOpenGLWidget):
    """Panel for rendering the 3D world"""
    
    def __init__(self, parent):
        """Initialize the world view panel"""
        # Initialize OpenGL widget
        super(WorldViewPanel, self).__init__(parent)
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.world_view")
        self.logger.info("Initializing world view panel")
        
        # Store parent reference
        self.main_window = parent
        
        # Initialize scene and camera
        self.camera = Camera()
        self.scene = Scene(self)
        self.initialized = False
        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0
        
        # Mouse state
        self.mouse_x = 0
        self.mouse_y = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouse_down = False
        self.right_mouse_down = False
        
        # Camera control state
        self.move_forward = False
        self.move_backward = False
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False
        
        # Set focus policy to accept keyboard input
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Set up animation timer (60 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(16)  # ~60 FPS
        
        # Display simple starter world until login
        self.is_logged_in = False
        
        self.logger.info("World view panel initialized")
    
    def initializeGL(self):
        """Initialize OpenGL (called by Qt)"""
        self.logger.info("Initializing OpenGL")
        
        # Basic OpenGL settings
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Anti-aliasing
        glEnable(GL_MULTISAMPLE)
        
        # Initialize shaders and resources
        self.scene.initialize()
        
        # Setup camera
        self.camera.set_position(Vector3(128, 20, 128))
        self.camera.look_at(Vector3(128, 0, 128))
        
        self.initialized = True
    
    def resizeGL(self, width, height):
        """Handle resize event (called by Qt)"""
        # Update viewport
        glViewport(0, 0, width, height)
        
        # Update camera aspect ratio
        self.camera.set_aspect_ratio(width / height if height > 0 else 1.0)
    
    def paintGL(self):
        """Render the scene (called by Qt)"""
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Update camera 
        self.camera.update()
        
        # Render scene
        self.scene.render(self.camera)
        
        # Calculate FPS
        current_time = time.time()
        self.frame_count += 1
        
        if current_time - self.last_time >= 1.0:
            self.fps = self.frame_count
            self.main_window.update_status(f"FPS: {self.fps}", 2)
            self.frame_count = 0
            self.last_time = current_time
    
    def on_timer(self):
        """Handle timer event for animation"""
        # Process camera movement
        self.process_camera_movement()
        
        # Trigger a redraw
        self.update()
    
    def process_camera_movement(self):
        """Process camera movement from keyboard input"""
        # Skip if not logged in
        if not self.is_logged_in:
            return
            
        # Movement speed (units per second)
        speed = 5.0
        dt = 0.016  # Assume 16ms between frames
        
        # Apply movement
        if self.move_forward:
            self.camera.move_forward(speed * dt)
        if self.move_backward:
            self.camera.move_backward(speed * dt)
        if self.move_left:
            self.camera.move_left(speed * dt)
        if self.move_right:
            self.camera.move_right(speed * dt)
        if self.move_up:
            self.camera.move_up(speed * dt)
        if self.move_down:
            self.camera.move_down(speed * dt)
    
    def mousePressEvent(self, event):
        """Handle mouse button press events"""
        self.setFocus()  # Set focus to enable keyboard input
        
        if event.button() == Qt.LeftButton:
            self.mouse_down = True
            self.last_mouse_x = event.x()
            self.last_mouse_y = event.y()
            self.setCursor(Qt.BlankCursor)  # Hide cursor for better control
            self.grabMouse()  # Capture mouse to track outside widget
            
        elif event.button() == Qt.RightButton:
            self.right_mouse_down = True
            self.last_mouse_x = event.x()
            self.last_mouse_y = event.y()
            self.setCursor(Qt.BlankCursor)  # Hide cursor for better control
            self.grabMouse()  # Capture mouse to track outside widget
    
    def mouseReleaseEvent(self, event):
        """Handle mouse button release events"""
        if event.button() == Qt.LeftButton:
            self.mouse_down = False
            if not self.right_mouse_down:
                self.setCursor(Qt.ArrowCursor)  # Restore cursor
                self.releaseMouse()  # Release mouse capture
                
        elif event.button() == Qt.RightButton:
            self.right_mouse_down = False
            if not self.mouse_down:
                self.setCursor(Qt.ArrowCursor)  # Restore cursor
                self.releaseMouse()  # Release mouse capture
    
    def mouseMoveEvent(self, event):
        """Handle mouse motion"""
        # Get current mouse position
        x = event.x()
        y = event.y()
        
        # Calculate delta
        dx = x - self.last_mouse_x
        dy = y - self.last_mouse_y
        
        # Handle mouse drag when logged in
        if self.is_logged_in:
            if self.mouse_down:
                # Left drag - rotate camera
                self.camera.yaw(-dx * 0.5)
                self.camera.pitch(-dy * 0.5)
            elif self.right_mouse_down:
                # Right drag - pan camera
                self.camera.pan(-dx * 0.1, dy * 0.1)
        
        # Store current position
        self.last_mouse_x = x
        self.last_mouse_y = y
        
        # Reset cursor to center if mouse buttons are down (for continuous rotation/pan)
        if self.mouse_down or self.right_mouse_down:
            center_x = self.width() // 2
            center_y = self.height() // 2
            if abs(x - center_x) > 100 or abs(y - center_y) > 100:
                self.cursor().setPos(self.mapToGlobal(Qt.QPoint(center_x, center_y)))
                self.last_mouse_x = center_x
                self.last_mouse_y = center_y
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zoom"""
        if self.is_logged_in:
            # Get wheel rotation (in PyQt5, angleDelta() is used instead of wheelDelta())
            delta = event.angleDelta().y()
            
            # Zoom in/out
            zoom_factor = delta / 120.0  # 120 is the typical delta for one scroll unit
            self.camera.zoom(zoom_factor)
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        # Skip if not logged in
        if not self.is_logged_in:
            event.accept()
            return
            
        # Handle movement keys
        key = event.key()
        
        if key == Qt.Key_W:
            self.move_forward = True
        elif key == Qt.Key_S:
            self.move_backward = True
        elif key == Qt.Key_A:
            self.move_left = True
        elif key == Qt.Key_D:
            self.move_right = True
        elif key == Qt.Key_E or key == Qt.Key_Space:
            self.move_up = True
        elif key == Qt.Key_Q or key == Qt.Key_Shift:
            self.move_down = True
        else:
            # Let parent handle other keys
            super(WorldViewPanel, self).keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Handle key release events"""
        # Skip if not logged in
        if not self.is_logged_in:
            event.accept()
            return
            
        # Handle movement keys
        key = event.key()
        
        if key == Qt.Key_W:
            self.move_forward = False
        elif key == Qt.Key_S:
            self.move_backward = False
        elif key == Qt.Key_A:
            self.move_left = False
        elif key == Qt.Key_D:
            self.move_right = False
        elif key == Qt.Key_E or key == Qt.Key_Space:
            self.move_up = False
        elif key == Qt.Key_Q or key == Qt.Key_Shift:
            self.move_down = False
        else:
            # Let parent handle other keys
            super(WorldViewPanel, self).keyReleaseEvent(event)
    
    def on_login_success(self):
        """Handle successful login"""
        self.is_logged_in = True
        
        # Initialize the scene for the logged-in user
        self.scene.load_initial_scene()
        
        # Reset camera position
        self.camera.set_position(Vector3(128, 20, 128))
        self.camera.look_at(Vector3(128, 10, 128))
        
    def on_logout(self):
        """Handle logout"""
        self.is_logged_in = False
        
        # Reset scene to simple starter world
        self.scene.reset()