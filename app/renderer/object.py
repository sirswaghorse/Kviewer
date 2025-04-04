"""
Object renderer for the 3D scene.
Handles rendering of in-world objects (prims).
"""

import logging
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

from app.utils.vector import Vector3
from app.utils.matrix import Matrix4

class Object:
    """Class representing a 3D object in the scene"""
    
    def __init__(self, object_id):
        """Initialize the object"""
        self.logger = logging.getLogger("kitelyview.renderer.object")
        
        # Object identification
        self.object_id = object_id
        self.name = f"Object {object_id}"
        
        # Transform
        self.position = Vector3(0, 0, 0)
        self.rotation = [0.0, 0.0, 0.0, 1.0]  # Quaternion (x, y, z, w)
        self.scale = Vector3(1, 1, 1)
        
        # Appearance
        self.color = [1.0, 1.0, 1.0, 1.0]  # RGBA
        self.texture_id = None
        self.is_physical = False
        self.is_phantom = False
        self.is_temporary = False
        
        # Object type and parameters
        self.prim_type = "box"   # box, sphere, cylinder, torus, etc.
        self.params = {}         # Additional parameters specific to prim type
        
        # Display list for rendering
        self.display_list = None
        self.needs_update = True
        
        self.logger.debug(f"Object initialized with ID: {object_id}")
        
    def set_position(self, position):
        """Set object position"""
        self.position = position
        self.needs_update = True
        
    def set_rotation(self, x, y, z, w):
        """Set object rotation quaternion"""
        self.rotation = [x, y, z, w]
        self.needs_update = True
        
    def set_scale(self, scale):
        """Set object scale"""
        self.scale = scale
        self.needs_update = True
        
    def set_color(self, r, g, b, a=1.0):
        """Set object color"""
        self.color = [r, g, b, a]
        self.needs_update = True
        
    def set_texture(self, texture_id):
        """Set object texture"""
        self.texture_id = texture_id
        self.needs_update = True
        
    def set_prim_type(self, prim_type, params=None):
        """Set primitive type and parameters"""
        self.prim_type = prim_type
        self.params = params or {}
        self.needs_update = True
        
    def _update_display_list(self):
        """Update the display list for rendering"""
        # Clean up old display list
        if self.display_list is not None:
            glDeleteLists(self.display_list, 1)
            
        # Create new display list
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        
        # Set material properties
        glColor4f(*self.color)
        
        # Render based on prim type
        if self.prim_type == "box":
            self._render_box()
        elif self.prim_type == "sphere":
            self._render_sphere()
        elif self.prim_type == "cylinder":
            self._render_cylinder()
        elif self.prim_type == "torus":
            self._render_torus()
        elif self.prim_type == "prism":
            self._render_prism()
        else:
            # Default to box
            self._render_box()
            
        glEndList()
        
        # Clear update flag
        self.needs_update = False
        
    def _render_box(self):
        """Render a box primitive"""
        # Draw a simple box
        glBegin(GL_QUADS)
        
        # Front face
        glNormal3f(0, 0, 1)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        
        # Back face
        glNormal3f(0, 0, -1)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        
        # Top face
        glNormal3f(0, 1, 0)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        
        # Bottom face
        glNormal3f(0, -1, 0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        # Right face
        glNormal3f(1, 0, 0)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        
        # Left face
        glNormal3f(-1, 0, 0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        
        glEnd()
        
    def _render_sphere(self):
        """Render a sphere primitive"""
        # Draw a sphere
        sphere = gluNewQuadric()
        gluQuadricNormals(sphere, GLU_SMOOTH)
        gluQuadricTexture(sphere, GL_TRUE)
        gluSphere(sphere, 0.5, 24, 24)
        gluDeleteQuadric(sphere)
        
    def _render_cylinder(self):
        """Render a cylinder primitive"""
        # Draw a cylinder
        cylinder = gluNewQuadric()
        gluQuadricNormals(cylinder, GLU_SMOOTH)
        gluQuadricTexture(cylinder, GL_TRUE)
        
        # Create and position cylinder
        glPushMatrix()
        glRotatef(90, 1, 0, 0)  # Rotate to stand upright
        
        # Draw cylinder body
        gluCylinder(cylinder, 0.5, 0.5, 1.0, 24, 1)
        
        # Draw top cap
        glPushMatrix()
        glTranslatef(0, 0, 1.0)
        disk = gluNewQuadric()
        gluQuadricNormals(disk, GLU_SMOOTH)
        gluQuadricTexture(disk, GL_TRUE)
        gluDisk(disk, 0, 0.5, 24, 1)
        gluDeleteQuadric(disk)
        glPopMatrix()
        
        # Draw bottom cap
        glPushMatrix()
        glRotatef(180, 1, 0, 0)
        disk = gluNewQuadric()
        gluQuadricNormals(disk, GLU_SMOOTH)
        gluQuadricTexture(disk, GL_TRUE)
        gluDisk(disk, 0, 0.5, 24, 1)
        gluDeleteQuadric(disk)
        glPopMatrix()
        
        glPopMatrix()
        
        gluDeleteQuadric(cylinder)
        
    def _render_torus(self):
        """Render a torus primitive"""
        # Draw a torus using GL_QUAD_STRIP
        # This is a simplified torus implementation
        # In a full viewer, you'd use a more optimized approach
        
        major_radius = 0.3
        minor_radius = 0.1
        major_segments = 24
        minor_segments = 12
        
        for i in range(major_segments):
            theta1 = i * 2.0 * math.pi / major_segments
            theta2 = (i + 1) * 2.0 * math.pi / major_segments
            
            glBegin(GL_QUAD_STRIP)
            
            for j in range(minor_segments + 1):
                phi = j * 2.0 * math.pi / minor_segments
                
                # First point (theta1)
                # Calculate position
                x1 = (major_radius + minor_radius * math.cos(phi)) * math.cos(theta1)
                y1 = minor_radius * math.sin(phi)
                z1 = (major_radius + minor_radius * math.cos(phi)) * math.sin(theta1)
                
                # Calculate normal
                nx1 = math.cos(phi) * math.cos(theta1)
                ny1 = math.sin(phi)
                nz1 = math.cos(phi) * math.sin(theta1)
                
                # Second point (theta2)
                x2 = (major_radius + minor_radius * math.cos(phi)) * math.cos(theta2)
                y2 = minor_radius * math.sin(phi)
                z2 = (major_radius + minor_radius * math.cos(phi)) * math.sin(theta2)
                
                # Calculate normal
                nx2 = math.cos(phi) * math.cos(theta2)
                ny2 = math.sin(phi)
                nz2 = math.cos(phi) * math.sin(theta2)
                
                # Set normal and vertex for first point
                glNormal3f(nx1, ny1, nz1)
                glVertex3f(x1, y1, z1)
                
                # Set normal and vertex for second point
                glNormal3f(nx2, ny2, nz2)
                glVertex3f(x2, y2, z2)
                
            glEnd()
            
    def _render_prism(self):
        """Render a prism primitive"""
        # Draw a simple triangular prism
        # OpenSim supports various prism types, but we'll start with triangular
        
        # Number of sides for the prism base
        sides = 3
        
        # Vertices of the base polygon
        base_vertices = []
        for i in range(sides):
            angle = 2.0 * math.pi * i / sides
            x = 0.5 * math.cos(angle)
            z = 0.5 * math.sin(angle)
            base_vertices.append((x, z))
            
        # Draw top and bottom faces
        for y_coord in [-0.5, 0.5]:
            # Determine winding order based on which face we're drawing
            # to ensure normals point outward
            if y_coord > 0:
                glNormal3f(0, 1, 0)  # Normal for top face
                # Draw top face (counter-clockwise)
                glBegin(GL_POLYGON)
                for x, z in base_vertices:
                    glVertex3f(x, y_coord, z)
                glEnd()
            else:
                glNormal3f(0, -1, 0)  # Normal for bottom face
                # Draw bottom face (clockwise to flip normal)
                glBegin(GL_POLYGON)
                for x, z in reversed(base_vertices):
                    glVertex3f(x, y_coord, z)
                glEnd()
                
        # Draw side faces (quads connecting top and bottom)
        glBegin(GL_QUADS)
        for i in range(sides):
            # Get current and next vertex
            x1, z1 = base_vertices[i]
            x2, z2 = base_vertices[(i + 1) % sides]
            
            # Calculate face normal (simplified)
            nx = z1 - z2
            nz = x2 - x1
            length = math.sqrt(nx*nx + nz*nz)
            nx /= length
            nz /= length
            
            # Set normal
            glNormal3f(nx, 0, nz)
            
            # Draw face (counter-clockwise)
            glVertex3f(x1, -0.5, z1)
            glVertex3f(x2, -0.5, z2)
            glVertex3f(x2, 0.5, z2)
            glVertex3f(x1, 0.5, z1)
            
        glEnd()
        
    def render(self):
        """Render the object"""
        # Update display list if needed
        if self.needs_update or self.display_list is None:
            self._update_display_list()
            
        # Set up modelview matrix for this object
        glPushMatrix()
        
        # Apply transformations (position, rotation, scale)
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Apply rotation (convert quaternion to rotation matrix)
        x, y, z, w = self.rotation
        
        # Simplified quaternion to axis-angle conversion
        # In a full implementation, you would use a proper quaternion class
        scale = math.sqrt(x*x + y*y + z*z)
        if scale > 0.0001:  # Avoid division by zero
            x /= scale
            y /= scale
            z /= scale
            angle = 2.0 * math.atan2(scale, w) * 180.0 / math.pi
            glRotatef(angle, x, y, z)
            
        # Apply scale
        glScalef(self.scale.x, self.scale.y, self.scale.z)
        
        # Render the object
        glCallList(self.display_list)
        
        # Restore modelview matrix
        glPopMatrix()
        
    def cleanup(self):
        """Clean up OpenGL resources"""
        if self.display_list is not None:
            glDeleteLists(self.display_list, 1)
            self.display_list = None
