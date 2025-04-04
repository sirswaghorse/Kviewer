"""
Mini map panel for the KitelyView application.
Displays a top-down view of the current region.
"""

import wx
import wx.lib.agw.floatspin as floatspin
import logging
import math
import random
import time
import threading

class MiniMapPanel(wx.Panel):
    """Panel for displaying mini map of the region"""
    
    def __init__(self, parent):
        """Initialize the mini map panel"""
        wx.Panel.__init__(self, parent)
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.mini_map")
        self.logger.info("Initializing mini map panel")
        
        # Store parent reference
        self.main_window = parent
        
        # Map settings
        self.map_size = 256  # Region size (OpenSim regions are typically 256x256)
        self.zoom = 1.0
        self.center_x = self.map_size / 2
        self.center_y = self.map_size / 2
        
        # Avatar positioning
        self.avatar_x = self.map_size / 2
        self.avatar_y = self.map_size / 2
        self.avatar_direction = 0  # In degrees, 0 is north/up
        
        # Other avatars and objects
        self.other_avatars = []  # List of {x, y, name} dictionaries
        
        # Map data
        self.map_data = None
        self.map_bitmap = None
        self.need_redraw = True
        
        # UI setup
        self._create_ui()
        
        # Bind events
        self.map_canvas.Bind(wx.EVT_PAINT, self.on_paint)
        self.map_canvas.Bind(wx.EVT_SIZE, self.on_size)
        self.map_canvas.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.map_canvas.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.map_canvas.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.map_canvas.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        
        self.zoom_slider.Bind(wx.EVT_SLIDER, self.on_zoom_change)
        
        # Create update timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        
        self.logger.info("Mini map panel initialized")
        
    def _create_ui(self):
        """Create UI elements"""
        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create map canvas
        self.map_canvas = wx.Window(self, size=(250, 250), style=wx.BORDER_SIMPLE)
        self.map_canvas.SetBackgroundColour(wx.Colour(50, 50, 50))
        main_sizer.Add(self.map_canvas, 1, wx.EXPAND | wx.ALL, 5)
        
        # Create controls sizer
        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Zoom controls
        zoom_label = wx.StaticText(self, label="Zoom:")
        self.zoom_slider = wx.Slider(
            self,
            value=10,  # Initial value (1.0)
            minValue=5,   # Min value (0.5)
            maxValue=50,  # Max value (5.0)
            style=wx.SL_HORIZONTAL
        )
        
        controls_sizer.Add(zoom_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        controls_sizer.Add(self.zoom_slider, 1, wx.EXPAND)
        
        main_sizer.Add(controls_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Create coordinate display
        coord_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.coord_text = wx.StaticText(self, label="X: 128, Y: 128")
        coord_sizer.Add(self.coord_text, 0, wx.ALIGN_CENTER)
        
        main_sizer.Add(coord_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Set sizer
        self.SetSizer(main_sizer)
        
    def on_paint(self, event):
        """Handle paint event for the map canvas"""
        dc = wx.BufferedPaintDC(self.map_canvas)
        self.draw_map(dc)
        
    def on_size(self, event):
        """Handle resize event"""
        # Force redraw on resize
        self.need_redraw = True
        self.map_canvas.Refresh()
        event.Skip()
        
    def draw_map(self, dc):
        """Draw the mini map"""
        # Get canvas size
        size = self.map_canvas.GetClientSize()
        width = size.width
        height = size.height
        
        # Clear background
        dc.SetBackground(wx.Brush(wx.Colour(50, 50, 50)))
        dc.Clear()
        
        # Draw map background
        if self.map_bitmap:
            # Calculate scaling and position
            scale = self.zoom
            map_width = self.map_size * scale
            map_height = self.map_size * scale
            
            # Calculate top-left corner of the map view
            offset_x = (width / 2) - (self.center_x * scale)
            offset_y = (height / 2) - (self.center_y * scale)
            
            # Draw the map bitmap
            dc.DrawBitmap(
                self.map_bitmap,
                int(offset_x),
                int(offset_y),
                useMask=False
            )
        else:
            # Draw placeholder grid
            self.draw_placeholder_grid(dc, width, height)
            
        # Draw other avatars
        for avatar in self.other_avatars:
            # Calculate position
            scale = self.zoom
            offset_x = (width / 2) - (self.center_x * scale)
            offset_y = (height / 2) - (self.center_y * scale)
            
            x = int(offset_x + (avatar["x"] * scale))
            y = int(offset_y + (avatar["y"] * scale))
            
            # Draw avatar marker
            dc.SetBrush(wx.Brush(wx.Colour(0, 200, 0)))
            dc.SetPen(wx.Pen(wx.Colour(0, 100, 0), 1))
            dc.DrawCircle(x, y, 3)
            
            # Draw name if close enough
            if self.zoom >= 1.0:
                dc.SetTextForeground(wx.Colour(200, 255, 200))
                dc.DrawText(avatar["name"], x + 5, y - 5)
        
        # Draw user's avatar
        scale = self.zoom
        offset_x = (width / 2) - (self.center_x * scale)
        offset_y = (height / 2) - (self.center_y * scale)
        
        x = int(offset_x + (self.avatar_x * scale))
        y = int(offset_y + (self.avatar_y * scale))
        
        # Draw avatar marker
        dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0)))
        dc.SetPen(wx.Pen(wx.Colour(100, 0, 0), 1))
        dc.DrawCircle(x, y, 5)
        
        # Draw direction indicator
        angle_rad = math.radians(self.avatar_direction)
        dir_x = x + int(10 * math.sin(angle_rad))
        dir_y = y - int(10 * math.cos(angle_rad))
        dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2))
        dc.DrawLine(x, y, dir_x, dir_y)
        
        # Draw region borders
        scale = self.zoom
        offset_x = (width / 2) - (self.center_x * scale)
        offset_y = (height / 2) - (self.center_y * scale)
        
        dc.SetPen(wx.Pen(wx.Colour(200, 200, 200), 1, wx.PENSTYLE_DOT))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        
        # Draw main region border
        dc.DrawRectangle(
            int(offset_x),
            int(offset_y),
            int(self.map_size * scale),
            int(self.map_size * scale)
        )
        
    def draw_placeholder_grid(self, dc, width, height):
        """Draw a placeholder grid when no map data is available"""
        # Get scale and offsets
        scale = self.zoom
        offset_x = (width / 2) - (self.center_x * scale)
        offset_y = (height / 2) - (self.center_y * scale)
        
        # Set up drawing
        dc.SetPen(wx.Pen(wx.Colour(100, 100, 100), 1, wx.PENSTYLE_DOT))
        
        # Draw grid lines
        grid_spacing = 32  # Draw line every 32 units
        
        # Vertical lines
        for x in range(0, self.map_size + 1, grid_spacing):
            x_pos = int(offset_x + (x * scale))
            dc.DrawLine(x_pos, int(offset_y), x_pos, int(offset_y + (self.map_size * scale)))
            
        # Horizontal lines
        for y in range(0, self.map_size + 1, grid_spacing):
            y_pos = int(offset_y + (y * scale))
            dc.DrawLine(int(offset_x), y_pos, int(offset_x + (self.map_size * scale)), y_pos)
            
        # Draw coordinates at intersections
        if scale >= 1.0:
            dc.SetTextForeground(wx.Colour(150, 150, 150))
            for x in range(0, self.map_size + 1, grid_spacing):
                for y in range(0, self.map_size + 1, grid_spacing):
                    x_pos = int(offset_x + (x * scale))
                    y_pos = int(offset_y + (y * scale))
                    if 0 <= x_pos < width and 0 <= y_pos < height:
                        dc.DrawText(f"{x},{y}", x_pos + 2, y_pos + 2)
    
    def create_placeholder_map(self):
        """Create a placeholder map bitmap"""
        # Create bitmap at 256x256 (1:1 scale)
        bitmap = wx.Bitmap(self.map_size, self.map_size)
        dc = wx.MemoryDC(bitmap)
        
        # Fill with base color
        dc.SetBackground(wx.Brush(wx.Colour(100, 150, 100)))
        dc.Clear()
        
        # Add some random terrain features
        for _ in range(50):
            x = random.randint(0, self.map_size - 1)
            y = random.randint(0, self.map_size - 1)
            size = random.randint(5, 20)
            color = wx.Colour(
                random.randint(70, 130),
                random.randint(120, 200),
                random.randint(70, 130)
            )
            dc.SetBrush(wx.Brush(color))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawCircle(x, y, size)
            
        # Add some roads or paths
        dc.SetPen(wx.Pen(wx.Colour(150, 150, 150), 3))
        
        # Horizontal road
        y = random.randint(50, self.map_size - 50)
        dc.DrawLine(0, y, self.map_size, y)
        
        # Vertical road
        x = random.randint(50, self.map_size - 50)
        dc.DrawLine(x, 0, x, self.map_size)
        
        # Add a few "buildings"
        for _ in range(10):
            x = random.randint(10, self.map_size - 30)
            y = random.randint(10, self.map_size - 30)
            width = random.randint(10, 30)
            height = random.randint(10, 30)
            color = wx.Colour(
                random.randint(150, 200),
                random.randint(150, 200),
                random.randint(150, 200)
            )
            dc.SetBrush(wx.Brush(color))
            dc.SetPen(wx.Pen(wx.Colour(50, 50, 50), 1))
            dc.DrawRectangle(x, y, width, height)
            
        # Release DC
        dc.SelectObject(wx.NullBitmap)
        
        return bitmap
        
    def on_mouse_down(self, event):
        """Handle mouse down event"""
        self.map_canvas.CaptureMouse()
        self.drag_start_x = event.GetX()
        self.drag_start_y = event.GetY()
        self.drag_center_x = self.center_x
        self.drag_center_y = self.center_y
        
    def on_mouse_up(self, event):
        """Handle mouse up event"""
        if self.map_canvas.HasCapture():
            self.map_canvas.ReleaseMouse()
            
    def on_mouse_motion(self, event):
        """Handle mouse motion event"""
        # Only process if dragging
        if event.Dragging() and event.LeftIsDown() and hasattr(self, 'drag_start_x'):
            # Calculate drag distance in screen space
            dx = event.GetX() - self.drag_start_x
            dy = event.GetY() - self.drag_start_y
            
            # Convert to map space
            scale = self.zoom
            map_dx = dx / scale
            map_dy = dy / scale
            
            # Update center position (move opposite to drag direction)
            self.center_x = self.drag_center_x - map_dx
            self.center_y = self.drag_center_y - map_dy
            
            # Ensure center stays within reasonable bounds
            self.center_x = max(0, min(self.map_size, self.center_x))
            self.center_y = max(0, min(self.map_size, self.center_y))
            
            # Redraw
            self.map_canvas.Refresh()
            
        # Update coordinate display if mouse is over map
        if not event.Dragging():
            # Get map coordinates under mouse
            size = self.map_canvas.GetClientSize()
            scale = self.zoom
            
            # Calculate map position
            map_x = self.center_x + ((event.GetX() - (size.width / 2)) / scale)
            map_y = self.center_y + ((event.GetY() - (size.height / 2)) / scale)
            
            # Update coordinate text if within map bounds
            if 0 <= map_x <= self.map_size and 0 <= map_y <= self.map_size:
                self.coord_text.SetLabel(f"X: {int(map_x)}, Y: {int(map_y)}")
            
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zoom"""
        # Get wheel rotation
        rotation = event.GetWheelRotation()
        
        # Adjust zoom
        zoom_step = 0.1 if rotation > 0 else -0.1
        new_zoom = self.zoom + zoom_step
        
        # Clamp zoom to reasonable values
        new_zoom = max(0.5, min(5.0, new_zoom))
        
        # Update zoom
        if new_zoom != self.zoom:
            self.zoom = new_zoom
            
            # Update zoom slider
            self.zoom_slider.SetValue(int(self.zoom * 10))
            
            # Redraw
            self.map_canvas.Refresh()
            
    def on_zoom_change(self, event):
        """Handle zoom slider change"""
        # Get new zoom value
        new_zoom = self.zoom_slider.GetValue() / 10.0
        
        # Update zoom
        if new_zoom != self.zoom:
            self.zoom = new_zoom
            
            # Redraw
            self.map_canvas.Refresh()
            
    def on_timer(self, event):
        """Handle timer event for updates"""
        # In a full implementation, this would update based on viewer state
        # For now, just reload if needed
        if self.need_redraw:
            self.map_canvas.Refresh()
            self.need_redraw = False
    
    def update_avatar_position(self, x, y, direction):
        """Update the user's avatar position"""
        self.avatar_x = x
        self.avatar_y = y
        self.avatar_direction = direction
        
        # Center map on avatar if tracking
        self.center_x = x
        self.center_y = y
        
        # Update coordinate text
        self.coord_text.SetLabel(f"X: {int(x)}, Y: {int(y)}")
        
        # Redraw
        self.map_canvas.Refresh()
        
    def update_other_avatars(self, avatars):
        """Update positions of other avatars"""
        self.other_avatars = avatars
        self.map_canvas.Refresh()
    
    def on_login_success(self):
        """Handle successful login"""
        # Create placeholder map
        self.map_bitmap = self.create_placeholder_map()
        
        # Set up sample avatars
        self.avatar_x = 128
        self.avatar_y = 128
        self.avatar_direction = 0
        
        self.other_avatars = [
            {"x": 100, "y": 100, "name": "User1"},
            {"x": 150, "y": 120, "name": "User2"},
            {"x": 90, "y": 180, "name": "User3"}
        ]
        
        # Center map on avatar
        self.center_x = self.avatar_x
        self.center_y = self.avatar_y
        
        # Start update timer (4 fps is enough for minimap)
        self.timer.Start(250)
        
        # Force redraw
        self.need_redraw = True
        self.map_canvas.Refresh()
        
    def on_logout(self):
        """Handle logout"""
        # Stop timer
        self.timer.Stop()
        
        # Clear map data
        self.map_bitmap = None
        self.other_avatars = []
        
        # Reset view
        self.avatar_x = self.map_size / 2
        self.avatar_y = self.map_size / 2
        self.center_x = self.map_size / 2
        self.center_y = self.map_size / 2
        self.zoom = 1.0
        self.zoom_slider.SetValue(10)
        
        # Force redraw
        self.need_redraw = True
        self.map_canvas.Refresh()
