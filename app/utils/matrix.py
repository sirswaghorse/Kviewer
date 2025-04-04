"""
Matrix classes for 3D math operations.
"""

import math
import numpy as np
from app.utils.vector import Vector3

class Matrix4:
    """4x4 matrix class for 3D transformations"""
    
    def __init__(self, data=None):
        """Initialize with 4x4 data array or identity matrix if None"""
        if data is None:
            # Create identity matrix
            self.data = np.identity(4, dtype=np.float32)
        else:
            # Use provided data
            self.data = np.array(data, dtype=np.float32).reshape(4, 4)
            
    def __str__(self):
        """String representation"""
        return f"Matrix4:\n{self.data}"
        
    def __mul__(self, other):
        """Matrix multiplication with another matrix"""
        if isinstance(other, Matrix4):
            result = Matrix4()
            result.data = np.matmul(self.data, other.data)
            return result
        raise TypeError("Can only multiply Matrix4 with another Matrix4")
        
    def transform_point(self, point):
        """Transform a Vector3 point by this matrix"""
        # Create homogeneous coordinate
        p = np.array([point.x, point.y, point.z, 1.0], dtype=np.float32)
        
        # Apply transformation
        result = np.matmul(self.data, p)
        
        # Convert back to Vector3
        if abs(result[3]) > 1e-6:
            w_inv = 1.0 / result[3]
            return Vector3(result[0] * w_inv, result[1] * w_inv, result[2] * w_inv)
        else:
            return Vector3(result[0], result[1], result[2])
            
    def transform_vector(self, vector):
        """Transform a Vector3 direction vector by this matrix (no translation)"""
        # Create homogeneous coordinate with w=0 for direction vector
        v = np.array([vector.x, vector.y, vector.z, 0.0], dtype=np.float32)
        
        # Apply transformation
        result = np.matmul(self.data, v)
        
        # Convert back to Vector3
        return Vector3(result[0], result[1], result[2])
            
    def determinant(self):
        """Calculate determinant of matrix"""
        return np.linalg.det(self.data)
        
    def inverse(self):
        """Return inverse of matrix"""
        try:
            inv_data = np.linalg.inv(self.data)
            return Matrix4(inv_data)
        except np.linalg.LinAlgError:
            raise ValueError("Matrix is singular and cannot be inverted")
            
    def transpose(self):
        """Return transpose of matrix"""
        return Matrix4(np.transpose(self.data))
            
    @classmethod
    def identity(cls):
        """Return identity matrix"""
        return cls()
        
    @classmethod
    def translation(cls, x, y, z):
        """Create translation matrix"""
        if isinstance(x, Vector3):
            # If first argument is a Vector3, use its components
            y, z = x.y, x.z
            x = x.x
            
        result = cls()
        result.data[0, 3] = x
        result.data[1, 3] = y
        result.data[2, 3] = z
        return result
        
    @classmethod
    def scaling(cls, x, y, z):
        """Create scaling matrix"""
        if isinstance(x, Vector3):
            # If first argument is a Vector3, use its components
            y, z = x.y, x.z
            x = x.x
            
        result = cls()
        result.data[0, 0] = x
        result.data[1, 1] = y
        result.data[2, 2] = z
        return result
        
    @classmethod
    def rotation_x(cls, angle):
        """Create rotation matrix around X axis"""
        c = math.cos(angle)
        s = math.sin(angle)
        
        result = cls()
        result.data[1, 1] = c
        result.data[1, 2] = -s
        result.data[2, 1] = s
        result.data[2, 2] = c
        return result
        
    @classmethod
    def rotation_y(cls, angle):
        """Create rotation matrix around Y axis"""
        c = math.cos(angle)
        s = math.sin(angle)
        
        result = cls()
        result.data[0, 0] = c
        result.data[0, 2] = s
        result.data[2, 0] = -s
        result.data[2, 2] = c
        return result
        
    @classmethod
    def rotation_z(cls, angle):
        """Create rotation matrix around Z axis"""
        c = math.cos(angle)
        s = math.sin(angle)
        
        result = cls()
        result.data[0, 0] = c
        result.data[0, 1] = -s
        result.data[1, 0] = s
        result.data[1, 1] = c
        return result
        
    @classmethod
    def rotation_axis(cls, axis, angle):
        """Create rotation matrix around arbitrary axis"""
        # Normalize axis
        axis = axis.normalize()
        x, y, z = axis.x, axis.y, axis.z
        
        c = math.cos(angle)
        s = math.sin(angle)
        t = 1.0 - c
        
        # Build rotation matrix
        result = cls()
        result.data[0, 0] = t * x * x + c
        result.data[0, 1] = t * x * y - s * z
        result.data[0, 2] = t * x * z + s * y
        
        result.data[1, 0] = t * x * y + s * z
        result.data[1, 1] = t * y * y + c
        result.data[1, 2] = t * y * z - s * x
        
        result.data[2, 0] = t * x * z - s * y
        result.data[2, 1] = t * y * z + s * x
        result.data[2, 2] = t * z * z + c
        
        return result
        
    @classmethod
    def look_at(cls, eye, target, up=None):
        """Create a view matrix (camera looking at target)"""
        if up is None:
            up = Vector3(0, 1, 0)  # Default up is Y axis
            
        # Calculate forward (z), right (x), and up (y) vectors
        forward = (target - eye).normalize()
        right = forward.cross(up).normalize()
        up = right.cross(forward).normalize()
        
        # Create rotation part
        result = cls()
        result.data[0, 0] = right.x
        result.data[0, 1] = right.y
        result.data[0, 2] = right.z
        
        result.data[1, 0] = up.x
        result.data[1, 1] = up.y
        result.data[1, 2] = up.z
        
        result.data[2, 0] = -forward.x
        result.data[2, 1] = -forward.y
        result.data[2, 2] = -forward.z
        
        # Translation part
        result.data[0, 3] = -right.dot(eye)
        result.data[1, 3] = -up.dot(eye)
        result.data[2, 3] = forward.dot(eye)
        
        return result
        
    @classmethod
    def perspective(cls, fov, aspect, near, far):
        """Create perspective projection matrix"""
        tan_half_fov = math.tan(fov / 2.0)
        
        result = cls()
        result.data.fill(0.0)  # Zero out matrix
        
        result.data[0, 0] = 1.0 / (aspect * tan_half_fov)
        result.data[1, 1] = 1.0 / tan_half_fov
        result.data[2, 2] = -(far + near) / (far - near)
        result.data[2, 3] = -2.0 * far * near / (far - near)
        result.data[3, 2] = -1.0
        
        return result
        
    @classmethod
    def orthographic(cls, left, right, bottom, top, near, far):
        """Create orthographic projection matrix"""
        result = cls()
        result.data.fill(0.0)  # Zero out matrix
        
        result.data[0, 0] = 2.0 / (right - left)
        result.data[1, 1] = 2.0 / (top - bottom)
        result.data[2, 2] = -2.0 / (far - near)
        
        result.data[0, 3] = -(right + left) / (right - left)
        result.data[1, 3] = -(top + bottom) / (top - bottom)
        result.data[2, 3] = -(far + near) / (far - near)
        result.data[3, 3] = 1.0
        
        return result