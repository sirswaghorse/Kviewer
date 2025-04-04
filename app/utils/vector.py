"""
Vector utilities for KitelyView.
"""

import math
import numpy as np

class Vector3:
    """3D vector class with common operations"""
    
    def __init__(self, x=0.0, y=0.0, z=0.0):
        """Initialize from components"""
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    @classmethod
    def from_list(cls, values):
        """Create vector from list or array"""
        if len(values) >= 3:
            return cls(values[0], values[1], values[2])
        elif len(values) == 2:
            return cls(values[0], values[1], 0.0)
        elif len(values) == 1:
            return cls(values[0], 0.0, 0.0)
        return cls()
    
    def to_list(self):
        """Convert to list"""
        return [self.x, self.y, self.z]
    
    def to_numpy(self):
        """Convert to numpy array"""
        return np.array([self.x, self.y, self.z], dtype=np.float32)
    
    def __add__(self, other):
        """Vector addition"""
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        raise TypeError("Can only add another Vector3")
    
    def __sub__(self, other):
        """Vector subtraction"""
        if isinstance(other, Vector3):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        raise TypeError("Can only subtract another Vector3")
    
    def __mul__(self, scalar):
        """Scalar multiplication"""
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar):
        """Scalar multiplication (reverse)"""
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        """Scalar division"""
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def __neg__(self):
        """Negation"""
        return Vector3(-self.x, -self.y, -self.z)
    
    def __eq__(self, other):
        """Equality test"""
        if not isinstance(other, Vector3):
            return False
        return (self.x == other.x and self.y == other.y and self.z == other.z)
    
    def __str__(self):
        """String representation"""
        return f"({self.x}, {self.y}, {self.z})"
    
    def __repr__(self):
        """Detailed string representation"""
        return f"Vector3({self.x}, {self.y}, {self.z})"
    
    def dot(self, other):
        """Dot product"""
        if not isinstance(other, Vector3):
            raise TypeError("Can only compute dot product with another Vector3")
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        """Cross product"""
        if not isinstance(other, Vector3):
            raise TypeError("Can only compute cross product with another Vector3")
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def length(self):
        """Vector length"""
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def length_squared(self):
        """Squared vector length (faster)"""
        return self.x * self.x + self.y * self.y + self.z * self.z
    
    def normalize(self):
        """Normalize vector (in place)"""
        length = self.length()
        if length > 0:
            self.x /= length
            self.y /= length
            self.z /= length
        return self
    
    def normalized(self):
        """Return normalized vector (new instance)"""
        length = self.length()
        if length > 0:
            return Vector3(self.x / length, self.y / length, self.z / length)
        return Vector3(0, 0, 0)
    
    def distance(self, other):
        """Distance to another vector"""
        if not isinstance(other, Vector3):
            raise TypeError("Can only compute distance to another Vector3")
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)
    
    def angle(self, other):
        """Angle between vectors in radians"""
        if not isinstance(other, Vector3):
            raise TypeError("Can only compute angle with another Vector3")
        len1 = self.length()
        len2 = other.length()
        if len1 == 0 or len2 == 0:
            return 0
        dot = self.dot(other) / (len1 * len2)
        # Clamp dot product to [-1, 1] to avoid precision errors
        dot = max(-1, min(1, dot))
        return math.acos(dot)
    
    def lerp(self, other, t):
        """Linear interpolation between vectors"""
        if not isinstance(other, Vector3):
            raise TypeError("Can only interpolate with another Vector3")
        t = max(0, min(1, t))  # Clamp t to [0, 1]
        return Vector3(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t
        )


class Vector2:
    """2D vector class with common operations"""
    
    def __init__(self, x=0.0, y=0.0):
        """Initialize from components"""
        self.x = float(x)
        self.y = float(y)
    
    @classmethod
    def from_list(cls, values):
        """Create vector from list or array"""
        if len(values) >= 2:
            return cls(values[0], values[1])
        elif len(values) == 1:
            return cls(values[0], 0.0)
        return cls()
    
    def to_list(self):
        """Convert to list"""
        return [self.x, self.y]
    
    def to_numpy(self):
        """Convert to numpy array"""
        return np.array([self.x, self.y], dtype=np.float32)
    
    def __add__(self, other):
        """Vector addition"""
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        raise TypeError("Can only add another Vector2")
    
    def __sub__(self, other):
        """Vector subtraction"""
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        raise TypeError("Can only subtract another Vector2")
    
    def __mul__(self, scalar):
        """Scalar multiplication"""
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar):
        """Scalar multiplication (reverse)"""
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        """Scalar division"""
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")
        return Vector2(self.x / scalar, self.y / scalar)
    
    def __neg__(self):
        """Negation"""
        return Vector2(-self.x, -self.y)
    
    def __eq__(self, other):
        """Equality test"""
        if not isinstance(other, Vector2):
            return False
        return (self.x == other.x and self.y == other.y)
    
    def __str__(self):
        """String representation"""
        return f"({self.x}, {self.y})"
    
    def __repr__(self):
        """Detailed string representation"""
        return f"Vector2({self.x}, {self.y})"
    
    def dot(self, other):
        """Dot product"""
        if not isinstance(other, Vector2):
            raise TypeError("Can only compute dot product with another Vector2")
        return self.x * other.x + self.y * other.y
    
    def length(self):
        """Vector length"""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def length_squared(self):
        """Squared vector length (faster)"""
        return self.x * self.x + self.y * self.y
    
    def normalize(self):
        """Normalize vector (in place)"""
        length = self.length()
        if length > 0:
            self.x /= length
            self.y /= length
        return self
    
    def normalized(self):
        """Return normalized vector (new instance)"""
        length = self.length()
        if length > 0:
            return Vector2(self.x / length, self.y / length)
        return Vector2(0, 0)
    
    def distance(self, other):
        """Distance to another vector"""
        if not isinstance(other, Vector2):
            raise TypeError("Can only compute distance to another Vector2")
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)
    
    def angle(self, other):
        """Angle between vectors in radians"""
        if not isinstance(other, Vector2):
            raise TypeError("Can only compute angle with another Vector2")
        len1 = self.length()
        len2 = other.length()
        if len1 == 0 or len2 == 0:
            return 0
        dot = self.dot(other) / (len1 * len2)
        # Clamp dot product to [-1, 1] to avoid precision errors
        dot = max(-1, min(1, dot))
        return math.acos(dot)
    
    def lerp(self, other, t):
        """Linear interpolation between vectors"""
        if not isinstance(other, Vector2):
            raise TypeError("Can only interpolate with another Vector2")
        t = max(0, min(1, t))  # Clamp t to [0, 1]
        return Vector2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )
    
    def to_vector3(self, z=0.0):
        """Convert to a 3D vector"""
        return Vector3(self.x, self.y, z)