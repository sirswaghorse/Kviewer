"""
Camera class for 3D rendering.
Handles camera positioning, orientation, and projection.
"""

import math
from app.utils.vector import Vector3
from app.utils.matrix import Matrix4

class Camera:
    """Camera for 3D scene viewing"""
    
    def __init__(self):
        """Initialize the camera"""
        # Position and orientation
        self.position = Vector3(0, 0, 0)
        self.target = Vector3(0, 0, -1)
        self.up = Vector3(0, 1, 0)
        
        # Euler angles
        self.yaw_angle = 0.0    # Rotation around Y axis (left/right)
        self.pitch_angle = 0.0  # Rotation around X axis (up/down)
        self.roll_angle = 0.0   # Rotation around Z axis (tilt)
        
        # Perspective projection parameters
        self.fov = math.radians(60.0)  # 60 degrees field of view
        self.aspect_ratio = 4.0 / 3.0  # Default aspect ratio
        self.near_plane = 0.1
        self.far_plane = 1000.0
        
        # Camera matrices
        self.view_matrix = Matrix4.identity()
        self.projection_matrix = Matrix4.identity()
        
        # Update matrices
        self.update()
        
    def set_position(self, position):
        """Set camera position"""
        self.position = position
        self.update()
        
    def set_target(self, target):
        """Set camera target point"""
        self.target = target
        self._update_angles_from_vectors()
        self.update()
        
    def set_up(self, up):
        """Set camera up vector"""
        self.up = up.normalize()
        self.update()
        
    def look_at(self, target, up=None):
        """Point camera at a target"""
        self.target = target
        if up is not None:
            self.up = up.normalize()
            
        self._update_angles_from_vectors()
        self.update()
        
    def set_perspective(self, fov, aspect_ratio, near, far):
        """Set perspective projection parameters"""
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near_plane = near
        self.far_plane = far
        self._update_projection_matrix()
        
    def set_aspect_ratio(self, aspect_ratio):
        """Set aspect ratio"""
        self.aspect_ratio = aspect_ratio
        self._update_projection_matrix()
        
    def yaw(self, angle):
        """Rotate camera around Y axis (left/right)"""
        self.yaw_angle += math.radians(angle)
        self._update_vectors_from_angles()
        self.update()
        
    def pitch(self, angle):
        """Rotate camera around X axis (up/down)"""
        # Limit pitch to avoid gimbal lock
        new_pitch = self.pitch_angle + math.radians(angle)
        max_pitch = math.radians(89.0)
        self.pitch_angle = max(-max_pitch, min(max_pitch, new_pitch))
        self._update_vectors_from_angles()
        self.update()
        
    def roll(self, angle):
        """Rotate camera around Z axis (tilt)"""
        self.roll_angle += math.radians(angle)
        self._update_vectors_from_angles()
        self.update()
        
    def zoom(self, amount):
        """Zoom camera (change FOV)"""
        self.fov = max(math.radians(10.0), min(math.radians(170.0), self.fov - math.radians(amount * 2.0)))
        self._update_projection_matrix()
        
    def move_forward(self, distance):
        """Move camera forward in look direction"""
        forward = (self.target - self.position).normalize()
        self.position = self.position + forward * distance
        self.target = self.position + forward
        self.update()
        
    def move_backward(self, distance):
        """Move camera backward from look direction"""
        self.move_forward(-distance)
        
    def move_left(self, distance):
        """Move camera left (perpendicular to look direction)"""
        forward = (self.target - self.position).normalize()
        right = forward.cross(self.up).normalize()
        self.position = self.position - right * distance
        self.target = self.position + forward
        self.update()
        
    def move_right(self, distance):
        """Move camera right (perpendicular to look direction)"""
        self.move_left(-distance)
        
    def move_up(self, distance):
        """Move camera up (along world up vector)"""
        self.position = self.position + Vector3(0, 1, 0) * distance
        self.target = self.target + Vector3(0, 1, 0) * distance
        self.update()
        
    def move_down(self, distance):
        """Move camera down (along world up vector)"""
        self.move_up(-distance)
        
    def pan(self, dx, dy):
        """Pan camera (move target while keeping distance)"""
        forward = (self.target - self.position).normalize()
        right = forward.cross(self.up).normalize()
        up = right.cross(forward).normalize()
        
        distance = (self.target - self.position).length()
        
        self.target = self.target + right * dx + up * dy
        self.position = self.target - forward * distance
        
        self._update_angles_from_vectors()
        self.update()
        
    def update(self):
        """Update camera matrices"""
        self._update_view_matrix()
        self._update_projection_matrix()
        
    def reset(self):
        """Reset camera to default position and orientation"""
        self.position = Vector3(0, 0, 0)
        self.target = Vector3(0, 0, -1)
        self.up = Vector3(0, 1, 0)
        self.yaw_angle = 0.0
        self.pitch_angle = 0.0
        self.roll_angle = 0.0
        self.update()
        
    def _update_view_matrix(self):
        """Update the view matrix from camera position and orientation"""
        self.view_matrix = Matrix4.look_at(self.position, self.target, self.up)
        
    def _update_projection_matrix(self):
        """Update the projection matrix from camera parameters"""
        self.projection_matrix = Matrix4.perspective(
            self.fov, 
            self.aspect_ratio, 
            self.near_plane, 
            self.far_plane
        )
        
    def _update_vectors_from_angles(self):
        """Update camera vectors from Euler angles"""
        # Calculate new direction vector
        direction = Vector3(
            math.cos(self.pitch_angle) * math.sin(self.yaw_angle),
            math.sin(self.pitch_angle),
            math.cos(self.pitch_angle) * math.cos(self.yaw_angle)
        )
        
        # Set target position based on direction
        self.target = self.position + direction
        
        # Handle roll by adjusting up vector
        if abs(self.roll_angle) > 0.001:
            # Calculate right vector
            right = direction.cross(Vector3(0, 1, 0)).normalize()
            
            # Calculate up vector with roll applied
            self.up = right.cross(direction).normalize()
            self.up = self.up.rotate_around_axis(direction, self.roll_angle)
        else:
            # Standard up vector without roll
            right = direction.cross(Vector3(0, 1, 0)).normalize()
            self.up = right.cross(direction).normalize()
        
    def _update_angles_from_vectors(self):
        """Update Euler angles from camera vectors"""
        # Calculate direction vector
        direction = (self.target - self.position).normalize()
        
        # Calculate yaw and pitch
        self.yaw_angle = math.atan2(direction.x, direction.z)
        self.pitch_angle = math.asin(direction.y)
        
        # Calculate roll (this is approximate)
        forward = direction
        right = forward.cross(Vector3(0, 1, 0)).normalize()
        std_up = right.cross(forward).normalize()
        
        # Dot product to find angle between standard up and actual up
        dot = std_up.dot(self.up)
        if abs(dot) > 0.999:
            self.roll_angle = 0.0
        else:
            # Determine sign of the roll angle
            cross = std_up.cross(self.up)
            sign = 1.0 if cross.dot(forward) > 0.0 else -1.0
            self.roll_angle = math.acos(dot) * sign