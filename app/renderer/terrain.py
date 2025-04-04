"""
Terrain renderer for the 3D scene.
Handles heightmap-based terrain rendering.
"""

import logging
import math
import random
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

from app.utils.vector import Vector3

class Terrain:
    """Terrain renderer for OpenSimulator regions"""
    
    def __init__(self, width, height):
        """Initialize terrain with given dimensions"""
        self.logger = logging.getLogger("kitelyview.renderer.terrain")
        
        # Terrain dimensions
        self.width = width
        self.height = height
        
        # Heightmap data (grid of height values)
        self.heightmap = np.zeros((width + 1, height + 1), dtype=np.float32)
        
        # Terrain settings
        self.scale_x = 1.0  # X scale (meters per grid unit)
        self.scale_y = 1.0  # Y scale (height scale)
        self.scale_z = 1.0  # Z scale (meters per grid unit)
        
        # Rendering settings
        self.detail_level = 1    # Detail level (1 = highest)
        self.water_height = 20.0  # Water height in meters
        
        # Display lists for rendering
        self.terrain_dl = None
        self.water_dl = None
        
        # Colors
        self.water_color = [0.0, 0.3, 0.5, 0.7]  # RGBA
        
        # Flag to track if terrain needs regenerating
        self.needs_update = True
        
        self.logger.info(f"Terrain initialized with dimensions {width}x{height}")
        
    def generate_random_terrain(self):
        """Generate a random terrain for testing"""
        self.logger.info("Generating random terrain")
        
        # Create a simple terrain with hills and valleys
        for x in range(self.width + 1):
            for z in range(self.height + 1):
                # Base height
                base_height = 0.0
                
                # Add some large features
                base_height += 30.0 * math.sin(x / 30.0) * math.sin(z / 30.0)
                
                # Add some medium features
                base_height += 5.0 * math.sin(x / 10.0 + 0.5) * math.sin(z / 10.0 + 0.5)
                
                # Add some small features
                base_height += 1.0 * math.sin(x / 5.0 + 1.0) * math.sin(z / 5.0 + 1.0)
                
                # Add some random noise
                base_height += random.uniform(-0.5, 0.5)
                
                # Ensure minimum height is above water
                self.heightmap[x, z] = max(self.water_height - 5.0, base_height + 20.0)
                
        # Set flag to update display lists
        self.needs_update = True
        
        self.logger.info("Random terrain generated")
        
    def update_from_data(self, terrain_data):
        """Update terrain from simulator data"""
        self.logger.info("Updating terrain from simulator data")
        
        try:
            # Parse terrain data
            # This would normally extract heightmap data from the simulator packet
            # For now, we'll just log it
            self.logger.debug(f"Received terrain data: {len(terrain_data)} bytes")
            
            # Set flag to update display lists
            self.needs_update = True
            
        except Exception as e:
            self.logger.error(f"Error updating terrain from data: {e}", exc_info=True)
            
    def reset(self):
        """Reset terrain to flat state"""
        self.logger.info("Resetting terrain")
        
        # Reset heightmap to zero
        self.heightmap.fill(0.0)
        
        # Set flag to update display lists
        self.needs_update = True
        
    def _update_display_lists(self):
        """Update the display lists for rendering"""
        self.logger.debug("Updating terrain display lists")
        
        # Clean up old display lists
        if self.terrain_dl is not None:
            glDeleteLists(self.terrain_dl, 1)
            
        if self.water_dl is not None:
            glDeleteLists(self.water_dl, 1)
            
        # Create terrain display list
        self.terrain_dl = glGenLists(1)
        glNewList(self.terrain_dl, GL_COMPILE)
        self._render_terrain_mesh()
        glEndList()
        
        # Create water display list
        self.water_dl = glGenLists(1)
        glNewList(self.water_dl, GL_COMPILE)
        self._render_water_plane()
        glEndList()
        
        # Clear update flag
        self.needs_update = False
        
    def _calculate_normal(self, x, z):
        """Calculate normal vector at given terrain coordinate"""
        # Handle edge cases
        if x <= 0 or x >= self.width or z <= 0 or z >= self.height:
            return Vector3(0, 1, 0)
            
        # Get height values
        h = self.heightmap[x, z]
        h_nx = self.heightmap[x-1, z]
        h_px = self.heightmap[x+1, z]
        h_nz = self.heightmap[x, z-1]
        h_pz = self.heightmap[x, z+1]
        
        # Calculate vectors along terrain grid
        v1 = Vector3(2.0, h_px - h_nx, 0.0)
        v2 = Vector3(0.0, h_pz - h_nz, 2.0)
        
        # Calculate normal using cross product
        normal = v1.cross(v2).normalize()
        return normal
        
    def _render_terrain_mesh(self):
        """Render the terrain mesh"""
        # Enable texturing and set material properties
        glEnable(GL_TEXTURE_2D)
        glColor3f(0.8, 0.8, 0.8)  # Default color multiplier
        
        # Set detail level (stride through heightmap)
        stride = self.detail_level
        
        # Render terrain in strips
        for z in range(0, self.height, stride):
            glBegin(GL_TRIANGLE_STRIP)
            
            for x in range(0, self.width + 1, stride):
                # Get heights and calculate normal
                h1 = self.heightmap[x, min(z + stride, self.height)]
                h2 = self.heightmap[x, z]
                
                # Calculate normals
                n1 = self._calculate_normal(x, min(z + stride, self.height))
                n2 = self._calculate_normal(x, z)
                
                # Set color based on height
                self._set_terrain_color(h1)
                
                # Vertex 1
                glNormal3f(n1.x, n1.y, n1.z)
                glVertex3f(x, h1, z + stride)
                
                # Set color based on height
                self._set_terrain_color(h2)
                
                # Vertex 2
                glNormal3f(n2.x, n2.y, n2.z)
                glVertex3f(x, h2, z)
                
            glEnd()
            
        glDisable(GL_TEXTURE_2D)
        
    def _set_terrain_color(self, height):
        """Set color based on terrain height"""
        if height < self.water_height + 0.1:
            # Sand color
            glColor3f(0.8, 0.7, 0.5)
        elif height < self.water_height + 5.0:
            # Grass color
            glColor3f(0.3, 0.5, 0.2)
        elif height < self.water_height + 20.0:
            # Forest color
            glColor3f(0.2, 0.4, 0.1)
        elif height < self.water_height + 40.0:
            # Rock color
            glColor3f(0.5, 0.5, 0.5)
        else:
            # Snow color
            glColor3f(0.9, 0.9, 0.9)
            
    def _render_water_plane(self):
        """Render the water plane"""
        # Set water material properties
        glColor4f(*self.water_color)
        
        # Create a simple quad covering the entire terrain
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)  # Water surface normal
        
        glVertex3f(0, self.water_height, 0)
        glVertex3f(self.width, self.water_height, 0)
        glVertex3f(self.width, self.water_height, self.height)
        glVertex3f(0, self.water_height, self.height)
        
        glEnd()
        
    def render(self):
        """Render the terrain"""
        # Update display lists if needed
        if self.needs_update or self.terrain_dl is None or self.water_dl is None:
            self._update_display_lists()
            
        # Render terrain
        glCallList(self.terrain_dl)
        
        # Set up for water rendering
        glEnable(GL_BLEND)
        glDepthMask(GL_FALSE)  # Don't write to depth buffer for transparent water
        
        # Render water
        glCallList(self.water_dl)
        
        # Restore state
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        
    def get_height(self, x, z):
        """Get terrain height at given world coordinates"""
        # Convert world coordinates to heightmap indices
        terrain_x = int(x)
        terrain_z = int(z)
        
        # Clamp to terrain boundaries
        terrain_x = max(0, min(self.width, terrain_x))
        terrain_z = max(0, min(self.height, terrain_z))
        
        # Return interpolated height
        return self.heightmap[terrain_x, terrain_z]
        
    def cleanup(self):
        """Clean up OpenGL resources"""
        if self.terrain_dl is not None:
            glDeleteLists(self.terrain_dl, 1)
            self.terrain_dl = None
            
        if self.water_dl is not None:
            glDeleteLists(self.water_dl, 1)
            self.water_dl = None
