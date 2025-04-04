"""
Avatar rendering for the 3D renderer.
Handles avatar appearance, animation, and attachments.
"""

import logging
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

from app.utils.vector import Vector3
from app.utils.matrix import Matrix4

class Avatar:
    """Avatar representation in the 3D scene"""
    
    def __init__(self, agent_id):
        """Initialize the avatar"""
        self.logger = logging.getLogger("kitelyview.renderer.avatar")
        
        # Store agent ID
        self.agent_id = agent_id
        
        # Position and orientation
        self.position = Vector3(128, 0, 128)  # Default to center of region
        self.rotation = [0.0, 0.0, 0.0, 1.0]  # Quaternion (x, y, z, w)
        
        # Avatar state
        self.is_flying = False
        self.is_sitting = False
        self.is_typing = False
        
        # Avatar appearance
        self.height = 1.8        # Default height in meters
        self.body_type = 0       # 0 = female, 1 = male
        self.skin_color = [0.9, 0.75, 0.65, 1.0]  # Default skin color (RGBA)
        
        # Animation state
        self.current_animation = "stand"  # Default animation
        self.animation_time = 0.0
        
        # Display list for avatar model
        self.display_list = None
        
        # Create display list for simple avatar representation
        self._create_display_list()
        
        self.logger.debug(f"Avatar initialized with ID: {agent_id}")
        
    def _create_display_list(self):
        """Create a display list for rendering the avatar"""
        # Create a simple avatar representation
        if self.display_list is None:
            self.display_list = glGenLists(1)
            
        glNewList(self.display_list, GL_COMPILE)
        
        # Set material properties
        glColor4f(*self.skin_color)
        
        # Draw a simple humanoid figure
        
        # Draw head (sphere)
        glPushMatrix()
        glTranslatef(0, self.height - 0.15, 0)
        sphere = gluNewQuadric()
        gluQuadricNormals(sphere, GLU_SMOOTH)
        gluSphere(sphere, 0.15, 16, 16)  # Head radius = 0.15
        gluDeleteQuadric(sphere)
        glPopMatrix()
        
        # Draw torso (cylinder)
        glPushMatrix()
        glTranslatef(0, self.height - 0.5, 0)
        glRotatef(90, 1, 0, 0)
        cylinder = gluNewQuadric()
        gluQuadricNormals(cylinder, GLU_SMOOTH)
        gluCylinder(cylinder, 0.15, 0.15, 0.4, 12, 1)  # Torso
        gluDeleteQuadric(cylinder)
        glPopMatrix()
        
        # Draw lower body (cone)
        glPushMatrix()
        glTranslatef(0, self.height - 0.9, 0)
        glRotatef(90, 1, 0, 0)
        cylinder = gluNewQuadric()
        gluQuadricNormals(cylinder, GLU_SMOOTH)
        gluCylinder(cylinder, 0.15, 0.1, 0.3, 12, 1)  # Lower body
        gluDeleteQuadric(cylinder)
        glPopMatrix()
        
        # Draw upper legs
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * 0.07, self.height - 1.2, 0)
            glRotatef(90, 1, 0, 0)
            cylinder = gluNewQuadric()
            gluQuadricNormals(cylinder, GLU_SMOOTH)
            gluCylinder(cylinder, 0.05, 0.05, 0.4, 8, 1)  # Upper leg
            gluDeleteQuadric(cylinder)
            glPopMatrix()
            
        # Draw lower legs
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * 0.07, self.height - 1.6, 0)
            glRotatef(90, 1, 0, 0)
            cylinder = gluNewQuadric()
            gluQuadricNormals(cylinder, GLU_SMOOTH)
            gluCylinder(cylinder, 0.05, 0.05, 0.4, 8, 1)  # Lower leg
            gluDeleteQuadric(cylinder)
            glPopMatrix()
            
        # Draw upper arms
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * 0.2, self.height - 0.3, 0)
            glRotatef(90, 0, 0, 1)
            glRotatef(90, 1, 0, 0)
            cylinder = gluNewQuadric()
            gluQuadricNormals(cylinder, GLU_SMOOTH)
            gluCylinder(cylinder, 0.04, 0.04, 0.3, 8, 1)  # Upper arm
            gluDeleteQuadric(cylinder)
            glPopMatrix()
            
        # Draw lower arms
        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * 0.5, self.height - 0.3, 0)
            glRotatef(90, 0, 0, 1)
            glRotatef(90, 1, 0, 0)
            cylinder = gluNewQuadric()
            gluQuadricNormals(cylinder, GLU_SMOOTH)
            gluCylinder(cylinder, 0.03, 0.03, 0.3, 8, 1)  # Lower arm
            gluDeleteQuadric(cylinder)
            glPopMatrix()
            
        glEndList()
        
    def set_position(self, position):
        """Set avatar position"""
        self.position = position
        
    def set_rotation(self, x, y, z, w):
        """Set avatar rotation quaternion"""
        self.rotation = [x, y, z, w]
        
    def set_animation(self, animation_name):
        """Set current animation"""
        self.current_animation = animation_name
        self.animation_time = 0.0
        
    def update_animation(self, delta_time):
        """Update animation time"""
        self.animation_time += delta_time
        
    def set_flying(self, is_flying):
        """Set flying state"""
        self.is_flying = is_flying
        
    def set_sitting(self, is_sitting):
        """Set sitting state"""
        self.is_sitting = is_sitting
        
    def set_typing(self, is_typing):
        """Set typing state"""
        self.is_typing = is_typing
        
    def set_appearance(self, appearance_data):
        """Set avatar appearance"""
        if "height" in appearance_data:
            self.height = appearance_data["height"]
            
        if "body_type" in appearance_data:
            self.body_type = appearance_data["body_type"]
            
        if "skin_color" in appearance_data:
            self.skin_color = appearance_data["skin_color"]
            
        # Regenerate the display list with new appearance
        self._create_display_list()
        
    def render(self):
        """Render the avatar"""
        if self.display_list is None:
            return
            
        # Calculate heading from quaternion
        # This is a simplified conversion from quaternion to heading angle
        x, y, z, w = self.rotation
        heading = math.degrees(2 * math.atan2(y, w))
        
        # Save model-view matrix
        glPushMatrix()
        
        # Position avatar
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Rotate avatar to face correct direction
        glRotatef(heading, 0, 1, 0)
        
        # Apply animation
        self._apply_animation()
        
        # Draw avatar
        glCallList(self.display_list)
        
        # Draw name tag above avatar
        self._draw_name_tag()
        
        # Restore model-view matrix
        glPopMatrix()
        
    def _apply_animation(self):
        """Apply current animation to avatar pose"""
        # This is a simplified implementation
        # In a full viewer, you would load and play actual animations
        
        if self.current_animation == "walk":
            # Simple walking animation - bob up and down slightly
            bob_amount = math.sin(self.animation_time * 5.0) * 0.05
            glTranslatef(0, bob_amount, 0)
            
        elif self.current_animation == "fly":
            # Simple flying animation - tilt forward slightly
            glRotatef(20, 1, 0, 0)
            
        elif self.current_animation == "sit":
            # Simple sitting animation - lower position and bend at waist
            glTranslatef(0, -0.5, 0)
            glRotatef(90, 1, 0, 0)
            
    def _draw_name_tag(self):
        """Draw name tag above avatar"""
        # In a full implementation, this would render actual text
        # For simplicity, we'll just draw a placeholder rectangle
        
        # This would be replaced with actual text rendering in a full viewer
        glPushMatrix()
        glTranslatef(0, self.height + 0.3, 0)
        
        # Make the name tag face the camera (billboarding)
        # This is a simplified implementation
        glRotatef(180, 0, 1, 0)
        
        # Draw a simple rectangle placeholder
        glDisable(GL_LIGHTING)
        glColor4f(1.0, 1.0, 1.0, 0.7)
        
        glBegin(GL_QUADS)
        glVertex3f(-0.2, 0.0, 0)
        glVertex3f(0.2, 0.0, 0)
        glVertex3f(0.2, 0.1, 0)
        glVertex3f(-0.2, 0.1, 0)
        glEnd()
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
        
    def cleanup(self):
        """Clean up resources"""
        if self.display_list is not None:
            glDeleteLists(self.display_list, 1)
            self.display_list = None
