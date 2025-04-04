"""
Scene management for 3D rendering.
Handles the overall scene, including objects, terrain, and lighting.
"""

import logging
import math
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from app.utils.vector import Vector3
from app.utils.matrix import Matrix4
from app.renderer.shader import ShaderProgram

class Scene:
    """Scene for 3D world rendering"""
    
    def __init__(self, parent):
        """Initialize the scene"""
        # Set up logging
        self.logger = logging.getLogger("kitelyview.renderer.scene")
        self.logger.info("Initializing scene")
        
        # Store parent reference
        self.parent = parent
        
        # Initialize OpenGL resources
        self.initialized = False
        self.shader = None
        
        # Scene data
        self.objects = []
        self.avatars = []
        
        # Terrain data
        self.terrain_mesh = None
        self.terrain_texture = None
        
        # Lighting
        self.light_position = Vector3(1000, 1000, 1000)  # Sun position
        self.light_color = (1.0, 1.0, 0.9)  # Slightly yellow sunlight
        self.ambient_light = (0.2, 0.2, 0.25)  # Slightly blue ambient
        
        # Sky and water
        self.sky_color = (0.5, 0.7, 1.0)
        self.water_level = 20.0
        self.water_color = (0.0, 0.4, 0.8, 0.5)
        
    def initialize(self):
        """Initialize OpenGL resources"""
        if self.initialized:
            return
            
        self.logger.info("Initializing scene OpenGL resources")
        
        # Create default shader program
        try:
            self.shader = ShaderProgram()
            self.shader.load_from_files("app/assets/shaders/default.vert", "app/assets/shaders/default.frag")
            self.shader.link()
        except Exception as e:
            self.logger.error(f"Failed to load shaders: {e}")
            # Fall back to fixed function pipeline
            self.shader = None
            
        # Initialize simple terrain for demo
        self._init_terrain()
        
        self.initialized = True
        
    def _init_terrain(self):
        """Initialize a simple terrain mesh"""
        # Create a simple procedural terrain (will be replaced with actual height map data)
        def height_function(x, z):
            """Simple height function for procedural terrain"""
            scale = 0.02
            height = 20.0 * (
                math.sin(x * scale) * math.cos(z * scale) +
                0.5 * math.sin(x * scale * 2) * math.cos(z * scale * 2) +
                0.25 * math.sin(x * scale * 4) * math.cos(z * scale * 4)
            )
            return max(1.0, height + 10.0)
            
        # Create terrain mesh
        self.terrain_vertices = []
        self.terrain_normals = []
        self.terrain_texcoords = []
        self.terrain_indices = []
        
        # Terrain parameters
        size = 256
        grid_size = 32
        scale = size / grid_size
        
        # Generate vertices, normals, and texture coordinates
        for z in range(grid_size + 1):
            for x in range(grid_size + 1):
                # Calculate position
                world_x = x * scale
                world_z = z * scale
                height = height_function(world_x, world_z)
                
                # Add vertex
                self.terrain_vertices.extend([world_x, height, world_z])
                
                # Calculate normal (using central differences)
                if x > 0 and x < grid_size and z > 0 and z < grid_size:
                    h_left = height_function(world_x - scale, world_z)
                    h_right = height_function(world_x + scale, world_z)
                    h_up = height_function(world_x, world_z - scale)
                    h_down = height_function(world_x, world_z + scale)
                    
                    # Calculate normal using cross product of tangent vectors
                    normal = Vector3(h_left - h_right, 2.0 * scale, h_up - h_down).normalize()
                else:
                    normal = Vector3(0, 1, 0)
                    
                self.terrain_normals.extend([normal.x, normal.y, normal.z])
                
                # Texture coordinates
                self.terrain_texcoords.extend([world_x / size, world_z / size])
                
        # Generate indices for triangle strip rendering
        for z in range(grid_size):
            for x in range(grid_size):
                # Calculate vertex indices
                a = z * (grid_size + 1) + x
                b = a + 1
                c = a + (grid_size + 1)
                d = c + 1
                
                # Add two triangles
                self.terrain_indices.extend([a, c, b])
                self.terrain_indices.extend([b, c, d])
                
    def load_initial_scene(self):
        """Load the initial scene for a logged-in user"""
        self.logger.info("Loading initial scene")
        # In a real application, this would load region data from the server
        # For now, we'll just use our simple procedural terrain
        
    def render(self, camera):
        """Render the scene with the given camera"""
        if not self.initialized:
            return
            
        # Apply camera transformations
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        perspective_m = camera.projection_matrix.data
        glMultMatrixf(perspective_m)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        view_m = camera.view_matrix.data
        glMultMatrixf(view_m)
        
        # Set up basic lighting if not using shaders
        if self.shader is None:
            self._setup_fixed_function_lighting()
            
        # Render sky (simple gradient for now)
        self._render_sky(camera)
        
        # Render terrain
        self._render_terrain()
        
        # Render water plane
        self._render_water()
        
        # Render objects
        for obj in self.objects:
            obj.render()
            
        # Render avatars
        for avatar in self.avatars:
            avatar.render()
            
    def _setup_fixed_function_lighting(self):
        """Set up fixed function lighting for non-shader rendering"""
        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Set light position and properties
        glLightfv(GL_LIGHT0, GL_POSITION, [self.light_position.x, self.light_position.y, self.light_position.z, 0.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [*self.light_color, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        
        # Set global ambient light
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [*self.ambient_light, 1.0])
        
    def _render_sky(self, camera):
        """Render a simple sky gradient"""
        # Disable depth testing for sky drawing
        glDisable(GL_DEPTH_TEST)
        
        # Draw a full-screen quad with gradient
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, 1, 0, 1, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable lighting for sky
        glDisable(GL_LIGHTING)
        
        # Draw gradient quad
        glBegin(GL_QUADS)
        # Bottom - darker blue
        glColor3f(self.sky_color[0] * 0.5, self.sky_color[1] * 0.5, self.sky_color[2] * 0.7)
        glVertex2f(0, 0)
        glVertex2f(1, 0)
        
        # Top - lighter blue
        glColor3f(self.sky_color[0], self.sky_color[1], self.sky_color[2])
        glVertex2f(1, 1)
        glVertex2f(0, 1)
        glEnd()
        
        # Restore matrices
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        # Re-enable depth testing
        glEnable(GL_DEPTH_TEST)
        
    def _render_terrain(self):
        """Render the terrain mesh"""
        if not self.terrain_vertices:
            return
            
        # Enable lighting if needed
        if self.shader is None:
            glEnable(GL_LIGHTING)
            
        # Set material properties
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.3, 0.5, 0.3, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 10.0)
        
        # Draw terrain using vertex arrays
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        
        glVertexPointer(3, GL_FLOAT, 0, self.terrain_vertices)
        glNormalPointer(GL_FLOAT, 0, self.terrain_normals)
        glTexCoordPointer(2, GL_FLOAT, 0, self.terrain_texcoords)
        
        # Draw the terrain
        glDrawElements(GL_TRIANGLES, len(self.terrain_indices), GL_UNSIGNED_INT, self.terrain_indices)
        
        # Disable vertex arrays
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        
    def _render_water(self):
        """Render a simple water plane"""
        # Enable transparency for water
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Disable lighting for simpler water
        glDisable(GL_LIGHTING)
        
        # Set water color
        glColor4f(*self.water_color)
        
        # Draw water plane
        size = 256.0
        glBegin(GL_QUADS)
        glVertex3f(0, self.water_level, 0)
        glVertex3f(size, self.water_level, 0)
        glVertex3f(size, self.water_level, size)
        glVertex3f(0, self.water_level, size)
        glEnd()
        
        # Reset state
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)
        
    def add_object(self, obj):
        """Add an object to the scene"""
        self.objects.append(obj)
        
    def remove_object(self, obj):
        """Remove an object from the scene"""
        if obj in self.objects:
            self.objects.remove(obj)
            
    def add_avatar(self, avatar):
        """Add an avatar to the scene"""
        self.avatars.append(avatar)
        
    def remove_avatar(self, avatar):
        """Remove an avatar from the scene"""
        if avatar in self.avatars:
            self.avatars.remove(avatar)
            
    def reset(self):
        """Reset the scene to its initial state"""
        self.objects.clear()
        self.avatars.clear()
        
    def cleanup(self):
        """Clean up resources"""
        if self.shader:
            self.shader.cleanup()
            
        # Other cleanup as needed