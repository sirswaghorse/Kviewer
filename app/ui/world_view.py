"""
World view panel for rendering the 3D OpenSimulator world.
"""

import wx
import wx.glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
import logging
import numpy as np
import time
import math
from app.renderer.camera import Camera
from app.renderer.scene import Scene
from app.utils.vector import Vector3
from app.utils.matrix import Matrix4

class WorldViewPanel(wx.glcanvas.GLCanvas):
    """Panel for rendering the 3D world"""
    
    def __init__(self, parent):
        """Initialize the world view panel"""
        # Initialize OpenGL canvas
        attribs = [
            wx.glcanvas.WX_GL_RGBA,
            wx.glcanvas.WX_GL_DOUBLEBUFFER,
            wx.glcanvas.WX_GL_DEPTH_SIZE, 24,
            wx.glcanvas.WX_GL_STENCIL_SIZE, 8,
            wx.glcanvas.WX_GL_SAMPLE_BUFFERS, 1,
            wx.glcanvas.WX_GL_SAMPLES, 4
        ]
        wx.glcanvas.GLCanvas.__init__(self, parent, attribList=attribs)
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.world_view")
        self.logger.info("Initializing world view panel")
        
        # Store parent reference
        self.main_window = parent
        
        # Create OpenGL context
        self.context = wx.glcanvas.GLContext(self)
        
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
        
        # Bind events
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_mouse_down)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_mouse_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        
        # Start render timer (60 FPS)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(16)  # ~60 FPS
        
        # Set focus to enable keyboard input
        self.SetFocus()
        
        # Display simple starter world until login
        self.is_logged_in = False
        
        self.logger.info("World view panel initialized")
    
    def init_gl(self):
        """Initialize OpenGL settings"""
        if self.initialized:
            return
            
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
    
    def on_size(self, event):
        """Handle resize event"""
        # Skip if not fully initialized
        if not self.initialized:
            event.Skip()
            return
            
        # Update viewport
        size = self.GetClientSize()
        
        if size.width > 0 and size.height > 0:
            # Set viewport to match window size
            self.SetCurrent(self.context)
            glViewport(0, 0, size.width, size.height)
            
            # Update camera aspect ratio
            self.camera.set_aspect_ratio(size.width / size.height)
        
        event.Skip()
    
    def on_paint(self, event):
        """Handle paint event"""
        # Set the OpenGL context
        self.SetCurrent(self.context)
        
        # Initialize OpenGL if needed
        if not self.initialized:
            self.init_gl()
            
        # Draw the scene
        self.render()
        
        # Swap buffers
        self.SwapBuffers()
    
    def on_erase_background(self, event):
        """Handle erase background - do nothing to avoid flicker"""
        pass
    
    def render(self):
        """Render the scene"""
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
    
    def on_timer(self, event):
        """Handle timer event for animation"""
        # Process camera movement
        self.process_camera_movement()
        
        # Trigger a redraw
        self.Refresh()
    
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
    
    def on_mouse_down(self, event):
        """Handle left mouse button down"""
        self.SetFocus()  # Set focus to enable keyboard input
        self.mouse_down = True
        self.last_mouse_x = event.GetX()
        self.last_mouse_y = event.GetY()
        self.CaptureMouse()  # Capture mouse to track outside window
    
    def on_mouse_up(self, event):
        """Handle left mouse button up"""
        self.mouse_down = False
        if self.HasCapture():
            self.ReleaseMouse()
    
    def on_right_mouse_down(self, event):
        """Handle right mouse button down"""
        self.SetFocus()  # Set focus to enable keyboard input
        self.right_mouse_down = True
        self.last_mouse_x = event.GetX()
        self.last_mouse_y = event.GetY()
        self.CaptureMouse()  # Capture mouse to track outside window
    
    def on_right_mouse_up(self, event):
        """Handle right mouse button up"""
        self.right_mouse_down = False
        if self.HasCapture() and not self.mouse_down:
            self.ReleaseMouse()
    
    def on_mouse_motion(self, event):
        """Handle mouse motion"""
        # Get current mouse position
        x = event.GetX()
        y = event.GetY()
        
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
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zoom"""
        if self.is_logged_in:
            # Get wheel rotation
            rotation = event.GetWheelRotation()
            
            # Zoom in/out
            zoom_factor = rotation / 120.0  # 120 is the typical delta for one scroll unit
            self.camera.zoom(zoom_factor)
    
    def on_key_down(self, event):
        """Handle key down event"""
        # Skip if not logged in
        if not self.is_logged_in:
            event.Skip()
            return
            
        # Handle movement keys
        key = event.GetKeyCode()
        
        if key == ord('W'):
            self.move_forward = True
        elif key == ord('S'):
            self.move_backward = True
        elif key == ord('A'):
            self.move_left = True
        elif key == ord('D'):
            self.move_right = True
        elif key == ord('E') or key == wx.WXK_SPACE:
            self.move_up = True
        elif key == ord('Q') or key == wx.WXK_SHIFT:
            self.move_down = True
        else:
            event.Skip()
    
    def on_key_up(self, event):
        """Handle key up event"""
        # Skip if not logged in
        if not self.is_logged_in:
            event.Skip()
            return
            
        # Handle movement keys
        key = event.GetKeyCode()
        
        if key == ord('W'):
            self.move_forward = False
        elif key == ord('S'):
            self.move_backward = False
        elif key == ord('A'):
            self.move_left = False
        elif key == ord('D'):
            self.move_right = False
        elif key == ord('E') or key == wx.WXK_SPACE:
            self.move_up = False
        elif key == ord('Q') or key == wx.WXK_SHIFT:
            self.move_down = False
        else:
            event.Skip()
    
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
