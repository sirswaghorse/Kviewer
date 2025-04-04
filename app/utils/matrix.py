"""
Matrix utilities for KitelyView.
"""

import math
import numpy as np
from .vector import Vector3, Vector2

class Matrix4:
    """4x4 matrix class with common operations for 3D transformations"""
    
    def __init__(self):
        """Initialize an identity matrix"""
        self.data = np.identity(4, dtype=np.float32)
    
    @classmethod
    def from_numpy(cls, array):
        """Create a matrix from a numpy array"""
        mat = cls()
        if array.shape == (4, 4):
            mat.data = array.astype(np.float32)
        return mat
    
    @classmethod
    def from_list(cls, values):
        """Create a matrix from a list (row-major order)"""
        mat = cls()
        if len(values) == 16:
            mat.data = np.array(values, dtype=np.float32).reshape(4, 4)
        return mat
    
    @classmethod
    def identity(cls):
        """Create an identity matrix"""
        return cls()
    
    @classmethod
    def zero(cls):
        """Create a zero matrix"""
        mat = cls()
        mat.data.fill(0)
        return mat
    
    @classmethod
    def translation(cls, x, y, z):
        """Create a translation matrix"""
        mat = cls()
        mat.data[0, 3] = x
        mat.data[1, 3] = y
        mat.data[2, 3] = z
        return mat
    
    @classmethod
    def translation_from_vector(cls, vector):
        """Create a translation matrix from a vector"""
        return cls.translation(vector.x, vector.y, vector.z)
    
    @classmethod
    def scaling(cls, x, y, z):
        """Create a scaling matrix"""
        mat = cls()
        mat.data[0, 0] = x
        mat.data[1, 1] = y
        mat.data[2, 2] = z
        return mat
    
    @classmethod
    def scaling_uniform(cls, scale):
        """Create a uniform scaling matrix"""
        return cls.scaling(scale, scale, scale)
    
    @classmethod
    def rotation_x(cls, angle_radians):
        """Create a rotation matrix around X axis"""
        mat = cls()
        c = math.cos(angle_radians)
        s = math.sin(angle_radians)
        mat.data[1, 1] = c
        mat.data[1, 2] = -s
        mat.data[2, 1] = s
        mat.data[2, 2] = c
        return mat
    
    @classmethod
    def rotation_y(cls, angle_radians):
        """Create a rotation matrix around Y axis"""
        mat = cls()
        c = math.cos(angle_radians)
        s = math.sin(angle_radians)
        mat.data[0, 0] = c
        mat.data[0, 2] = s
        mat.data[2, 0] = -s
        mat.data[2, 2] = c
        return mat
    
    @classmethod
    def rotation_z(cls, angle_radians):
        """Create a rotation matrix around Z axis"""
        mat = cls()
        c = math.cos(angle_radians)
        s = math.sin(angle_radians)
        mat.data[0, 0] = c
        mat.data[0, 1] = -s
        mat.data[1, 0] = s
        mat.data[1, 1] = c
        return mat
    
    @classmethod
    def from_axis_angle(cls, axis, angle_radians):
        """Create a rotation matrix from axis and angle"""
        mat = cls()
        
        # Normalize axis
        if isinstance(axis, Vector3):
            axis = axis.normalized()
            x, y, z = axis.x, axis.y, axis.z
        else:
            vec_len = math.sqrt(axis[0]*axis[0] + axis[1]*axis[1] + axis[2]*axis[2])
            if vec_len == 0:
                return mat
            x, y, z = axis[0]/vec_len, axis[1]/vec_len, axis[2]/vec_len
        
        c = math.cos(angle_radians)
        s = math.sin(angle_radians)
        t = 1.0 - c
        
        # Set up rotation matrix
        mat.data[0, 0] = t*x*x + c
        mat.data[0, 1] = t*x*y - z*s
        mat.data[0, 2] = t*x*z + y*s
        
        mat.data[1, 0] = t*x*y + z*s
        mat.data[1, 1] = t*y*y + c
        mat.data[1, 2] = t*y*z - x*s
        
        mat.data[2, 0] = t*x*z - y*s
        mat.data[2, 1] = t*y*z + x*s
        mat.data[2, 2] = t*z*z + c
        
        return mat
    
    @classmethod
    def from_quaternion(cls, quat):
        """Create a rotation matrix from quaternion [x, y, z, w]"""
        x, y, z, w = quat
        mat = cls()
        
        # Calculate coefficients
        xx = x * x
        xy = x * y
        xz = x * z
        xw = x * w
        
        yy = y * y
        yz = y * z
        yw = y * w
        
        zz = z * z
        zw = z * w
        
        # Set up rotation matrix
        mat.data[0, 0] = 1 - 2 * (yy + zz)
        mat.data[0, 1] = 2 * (xy - zw)
        mat.data[0, 2] = 2 * (xz + yw)
        
        mat.data[1, 0] = 2 * (xy + zw)
        mat.data[1, 1] = 1 - 2 * (xx + zz)
        mat.data[1, 2] = 2 * (yz - xw)
        
        mat.data[2, 0] = 2 * (xz - yw)
        mat.data[2, 1] = 2 * (yz + xw)
        mat.data[2, 2] = 1 - 2 * (xx + yy)
        
        return mat
    
    @classmethod
    def perspective(cls, fov, aspect, near, far):
        """Create a perspective projection matrix"""
        mat = cls.zero()
        
        # Convert FOV to radians
        if fov > math.pi:
            fov = math.radians(fov)
            
        tan_half_fov = math.tan(fov / 2)
        
        mat.data[0, 0] = 1.0 / (aspect * tan_half_fov)
        mat.data[1, 1] = 1.0 / tan_half_fov
        mat.data[2, 2] = -(far + near) / (far - near)
        mat.data[2, 3] = -1.0
        mat.data[3, 2] = -(2.0 * far * near) / (far - near)
        
        return mat
    
    @classmethod
    def orthographic(cls, left, right, bottom, top, near, far):
        """Create an orthographic projection matrix"""
        mat = cls.zero()
        
        mat.data[0, 0] = 2.0 / (right - left)
        mat.data[1, 1] = 2.0 / (top - bottom)
        mat.data[2, 2] = -2.0 / (far - near)
        
        mat.data[0, 3] = -(right + left) / (right - left)
        mat.data[1, 3] = -(top + bottom) / (top - bottom)
        mat.data[2, 3] = -(far + near) / (far - near)
        mat.data[3, 3] = 1.0
        
        return mat
    
    @classmethod
    def look_at(cls, eye, target, up):
        """Create a view matrix looking from eye position toward target"""
        mat = cls()
        
        # Convert to vectors if needed
        if not isinstance(eye, Vector3):
            eye = Vector3.from_list(eye)
        if not isinstance(target, Vector3):
            target = Vector3.from_list(target)
        if not isinstance(up, Vector3):
            up = Vector3.from_list(up)
        
        # Calculate axes
        forward = (target - eye).normalized()
        right = forward.cross(up).normalized()
        up = right.cross(forward)
        
        # Set rotation part
        mat.data[0, 0] = right.x
        mat.data[0, 1] = right.y
        mat.data[0, 2] = right.z
        
        mat.data[1, 0] = up.x
        mat.data[1, 1] = up.y
        mat.data[1, 2] = up.z
        
        mat.data[2, 0] = -forward.x
        mat.data[2, 1] = -forward.y
        mat.data[2, 2] = -forward.z
        
        # Set translation part
        mat.data[0, 3] = -right.dot(eye)
        mat.data[1, 3] = -up.dot(eye)
        mat.data[2, 3] = forward.dot(eye)
        
        return mat
    
    def __mul__(self, other):
        """Matrix multiplication"""
        if isinstance(other, Matrix4):
            result = Matrix4()
            result.data = np.matmul(self.data, other.data)
            return result
        elif isinstance(other, Vector3):
            # Transform a Vector3
            v = np.array([other.x, other.y, other.z, 1.0], dtype=np.float32)
            result = np.matmul(self.data, v)
            
            # Divide by w for perspective projection
            if result[3] != 0:
                result = result / result[3]
                
            return Vector3(result[0], result[1], result[2])
        else:
            raise TypeError("Can only multiply with Matrix4 or Vector3")
    
    def __eq__(self, other):
        """Equality test"""
        if not isinstance(other, Matrix4):
            return False
        return np.allclose(self.data, other.data)
    
    def __str__(self):
        """String representation"""
        return str(self.data)
    
    def __repr__(self):
        """Detailed string representation"""
        return f"Matrix4(\n{self.data}\n)"
    
    def get_row(self, row):
        """Get a row of the matrix"""
        return self.data[row].copy()
    
    def get_column(self, col):
        """Get a column of the matrix"""
        return self.data[:, col].copy()
    
    def transpose(self):
        """Get the transpose of this matrix"""
        result = Matrix4()
        result.data = np.transpose(self.data)
        return result
    
    def determinant(self):
        """Calculate the determinant of the matrix"""
        return np.linalg.det(self.data)
    
    def inverse(self):
        """Calculate the inverse of the matrix"""
        result = Matrix4()
        try:
            result.data = np.linalg.inv(self.data)
        except np.linalg.LinAlgError:
            # Fallback to identity for singular matrices
            result = Matrix4()
        return result
    
    def to_numpy(self):
        """Convert to a numpy array"""
        return self.data.copy()
    
    def to_list(self):
        """Convert to a list (row-major order)"""
        return self.data.flatten().tolist()
    
    def translate(self, x, y, z):
        """Apply a translation to this matrix"""
        translation = Matrix4.translation(x, y, z)
        return self * translation
    
    def rotate_x(self, angle_radians):
        """Apply a rotation around X axis to this matrix"""
        rotation = Matrix4.rotation_x(angle_radians)
        return self * rotation
    
    def rotate_y(self, angle_radians):
        """Apply a rotation around Y axis to this matrix"""
        rotation = Matrix4.rotation_y(angle_radians)
        return self * rotation
    
    def rotate_z(self, angle_radians):
        """Apply a rotation around Z axis to this matrix"""
        rotation = Matrix4.rotation_z(angle_radians)
        return self * rotation
    
    def rotate(self, axis, angle_radians):
        """Apply a rotation around an arbitrary axis to this matrix"""
        rotation = Matrix4.from_axis_angle(axis, angle_radians)
        return self * rotation
    
    def scale(self, x, y, z):
        """Apply a scaling to this matrix"""
        scaling = Matrix4.scaling(x, y, z)
        return self * scaling
    
    def scale_uniform(self, scale):
        """Apply a uniform scaling to this matrix"""
        scaling = Matrix4.scaling_uniform(scale)
        return self * scaling