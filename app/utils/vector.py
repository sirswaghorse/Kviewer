"""
Vector classes for 3D math operations.
"""

import math
import numpy as np

class Vector3:
    """3D vector class for math operations"""
    
    def __init__(self, x=0.0, y=0.0, z=0.0):
        """Initialize with x, y, z coordinates"""
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        
    def __add__(self, other):
        """Vector addition"""
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        
    def __sub__(self, other):
        """Vector subtraction"""
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        
    def __mul__(self, scalar):
        """Scalar multiplication"""
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
        
    def __truediv__(self, scalar):
        """Scalar division"""
        if scalar != 0:
            return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
        else:
            raise ZeroDivisionError("Cannot divide vector by zero")
            
    def __str__(self):
        """String representation"""
        return f"Vector3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
        
    def __eq__(self, other):
        """Equality comparison"""
        if isinstance(other, Vector3):
            return (
                abs(self.x - other.x) < 1e-6 and 
                abs(self.y - other.y) < 1e-6 and 
                abs(self.z - other.z) < 1e-6
            )
        return False
        
    def length(self):
        """Get vector magnitude"""
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        
    def length_squared(self):
        """Get squared vector magnitude (faster than length)"""
        return self.x * self.x + self.y * self.y + self.z * self.z
        
    def normalize(self):
        """Return normalized vector (unit length)"""
        length = self.length()
        if length > 0:
            return Vector3(self.x / length, self.y / length, self.z / length)
        return Vector3()
        
    def dot(self, other):
        """Dot product with another vector"""
        return self.x * other.x + self.y * other.y + self.z * other.z
        
    def cross(self, other):
        """Cross product with another vector"""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
        
    def distance_to(self, other):
        """Distance to another vector"""
        return (other - self).length()
        
    def angle_to(self, other):
        """Angle to another vector in radians"""
        if self.length() * other.length() == 0:
            return 0
        dot = max(-1.0, min(1.0, self.dot(other) / (self.length() * other.length())))
        return math.acos(dot)
        
    def rotate_around_axis(self, axis, angle):
        """Rotate this vector around an axis by an angle (in radians)"""
        # Normalize axis
        axis = axis.normalize()
        
        # Calculate rotation using quaternion formula
        sin_half = math.sin(angle / 2)
        cos_half = math.cos(angle / 2)
        
        # Quaternion components
        q_w = cos_half
        q_x = axis.x * sin_half
        q_y = axis.y * sin_half
        q_z = axis.z * sin_half
        
        # Apply quaternion rotation
        x = (
            (1 - 2*q_y*q_y - 2*q_z*q_z) * self.x +
            (2*q_x*q_y - 2*q_w*q_z) * self.y +
            (2*q_x*q_z + 2*q_w*q_y) * self.z
        )
        
        y = (
            (2*q_x*q_y + 2*q_w*q_z) * self.x +
            (1 - 2*q_x*q_x - 2*q_z*q_z) * self.y +
            (2*q_y*q_z - 2*q_w*q_x) * self.z
        )
        
        z = (
            (2*q_x*q_z - 2*q_w*q_y) * self.x +
            (2*q_y*q_z + 2*q_w*q_x) * self.y +
            (1 - 2*q_x*q_x - 2*q_y*q_y) * self.z
        )
        
        return Vector3(x, y, z)
        
    def to_tuple(self):
        """Convert to tuple"""
        return (self.x, self.y, self.z)
        
    def to_list(self):
        """Convert to list"""
        return [self.x, self.y, self.z]
        
    def to_numpy(self):
        """Convert to numpy array"""
        return np.array([self.x, self.y, self.z])
        
    @classmethod
    def from_tuple(cls, t):
        """Create from tuple"""
        return cls(t[0], t[1], t[2])
        
    @classmethod
    def from_list(cls, lst):
        """Create from list"""
        return cls(lst[0], lst[1], lst[2])
        
    @classmethod
    def from_numpy(cls, arr):
        """Create from numpy array"""
        return cls(arr[0], arr[1], arr[2])
        
    @classmethod
    def zero(cls):
        """Return zero vector"""
        return cls(0, 0, 0)
        
    @classmethod
    def one(cls):
        """Return vector with all components set to 1"""
        return cls(1, 1, 1)
        
    @classmethod
    def up(cls):
        """Return up vector (0, 1, 0)"""
        return cls(0, 1, 0)
        
    @classmethod
    def forward(cls):
        """Return forward vector (0, 0, 1)"""
        return cls(0, 0, 1)
        
    @classmethod
    def right(cls):
        """Return right vector (1, 0, 0)"""
        return cls(1, 0, 0)