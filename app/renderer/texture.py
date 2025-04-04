"""
Texture loading and management for the renderer.
Handles loading, binding, and managing OpenGL textures.
"""

import logging
import os
import numpy as np
from OpenGL.GL import *
from PIL import Image
import io

class Texture:
    """OpenGL texture wrapper"""
    
    def __init__(self, texture_id=None):
        """Initialize texture with optional existing texture ID"""
        self.logger = logging.getLogger("kitelyview.renderer.texture")
        
        # Texture state
        self.texture_id = texture_id or glGenTextures(1)
        self.width = 0
        self.height = 0
        self.channels = 0
        self.loaded = False
        self.target = GL_TEXTURE_2D
        
    def bind(self, texture_unit=GL_TEXTURE0):
        """Bind the texture to a texture unit"""
        glActiveTexture(texture_unit)
        glBindTexture(self.target, self.texture_id)
        
    def unbind(self):
        """Unbind the texture"""
        glBindTexture(self.target, 0)
        
    def load_from_file(self, file_path):
        """Load texture data from a file"""
        try:
            # Reset state if already loaded
            if self.loaded:
                self.width = 0
                self.height = 0
                self.channels = 0
                self.loaded = False
            
            # Check if file exists
            if not os.path.isfile(file_path):
                self.logger.error(f"Texture file not found: {file_path}")
                return False
                
            # Load image with PIL
            image = Image.open(file_path)
            
            # Store dimensions
            self.width = image.width
            self.height = image.height
            
            # Convert to RGBA
            if image.mode != "RGBA":
                image = image.convert("RGBA")
                self.channels = 4
            else:
                self.channels = len(image.getbands())
                
            # Flip image vertically (OpenGL expects textures upside down)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            
            # Get image data as bytes
            image_data = image.tobytes()
            
            # Upload to GPU
            self.bind()
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Upload image data
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                self.width,
                self.height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                image_data
            )
            
            # Generate mipmaps
            glGenerateMipmap(GL_TEXTURE_2D)
            
            # Clean up
            self.unbind()
            image.close()
            
            self.loaded = True
            self.logger.debug(f"Loaded texture from {file_path}: {self.width}x{self.height}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load texture from {file_path}: {e}", exc_info=True)
            return False
            
    def load_from_memory(self, image_data, width, height, channels=4):
        """Load texture from raw image data in memory"""
        try:
            # Reset state if already loaded
            if self.loaded:
                self.width = 0
                self.height = 0
                self.channels = 0
                self.loaded = False
                
            # Store dimensions
            self.width = width
            self.height = height
            self.channels = channels
            
            # Upload to GPU
            self.bind()
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Determine format based on channels
            internal_format = GL_RGBA
            pixel_format = GL_RGBA
            
            if channels == 1:
                internal_format = GL_RED
                pixel_format = GL_RED
            elif channels == 3:
                internal_format = GL_RGB
                pixel_format = GL_RGB
                
            # Upload image data
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                internal_format,
                self.width,
                self.height,
                0,
                pixel_format,
                GL_UNSIGNED_BYTE,
                image_data
            )
            
            # Generate mipmaps
            glGenerateMipmap(GL_TEXTURE_2D)
            
            # Clean up
            self.unbind()
            
            self.loaded = True
            self.logger.debug(f"Loaded texture from memory: {self.width}x{self.height}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load texture from memory: {e}", exc_info=True)
            return False
            
    def load_from_j2k(self, j2k_data):
        """Load texture from JPEG2000 data (common in OpenSim)"""
        try:
            # This would normally use a JPEG2000 library
            # Since this is complex, we'll use PIL which has limited J2K support
            # In a full viewer, you would use OpenJPEG or a dedicated J2K library
            
            # Create a buffer from the binary data
            buffer = io.BytesIO(j2k_data)
            
            # Load with PIL
            image = Image.open(buffer)
            
            # Convert to RGBA
            if image.mode != "RGBA":
                image = image.convert("RGBA")
                
            # Get dimensions
            self.width = image.width
            self.height = image.height
            self.channels = 4  # RGBA
            
            # Flip image vertically (OpenGL expects textures upside down)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            
            # Get image data as bytes
            image_data = image.tobytes()
            
            # Upload to GPU
            self.bind()
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Upload image data
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                self.width,
                self.height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                image_data
            )
            
            # Generate mipmaps
            glGenerateMipmap(GL_TEXTURE_2D)
            
            # Clean up
            self.unbind()
            image.close()
            
            self.loaded = True
            self.logger.debug(f"Loaded texture from J2K data: {self.width}x{self.height}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load texture from J2K data: {e}", exc_info=True)
            return False
            
    def create_default_texture(self):
        """Create a default checkerboard texture"""
        try:
            # Create a simple 64x64 checkerboard pattern
            self.width = 64
            self.height = 64
            self.channels = 4
            
            # Create checkerboard data
            data = np.zeros((self.height, self.width, self.channels), dtype=np.uint8)
            
            # Fill with checkerboard pattern
            for y in range(self.height):
                for x in range(self.width):
                    if (x // 8 + y // 8) % 2 == 0:
                        data[y, x] = [255, 255, 255, 255]  # White
                    else:
                        data[y, x] = [128, 128, 128, 255]  # Gray
                        
            # Upload to GPU
            self.bind()
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Upload image data
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                self.width,
                self.height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                data
            )
            
            # Generate mipmaps
            glGenerateMipmap(GL_TEXTURE_2D)
            
            # Clean up
            self.unbind()
            
            self.loaded = True
            self.logger.debug("Created default checkerboard texture")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create default texture: {e}", exc_info=True)
            return False
            
    def create_color_texture(self, r, g, b, a=1.0):
        """Create a single-color texture"""
        try:
            # Create a simple 1x1 texture with the specified color
            self.width = 1
            self.height = 1
            self.channels = 4
            
            # Create color data (1x1 pixel)
            color = [
                int(r * 255),
                int(g * 255),
                int(b * 255),
                int(a * 255)
            ]
            data = np.array([color], dtype=np.uint8)
            
            # Upload to GPU
            self.bind()
            
            # Set texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            # Upload image data
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                self.width,
                self.height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                data
            )
            
            # Clean up
            self.unbind()
            
            self.loaded = True
            self.logger.debug(f"Created color texture: ({r}, {g}, {b}, {a})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create color texture: {e}", exc_info=True)
            return False
            
    def cleanup(self):
        """Clean up OpenGL resources"""
        if self.loaded and self.texture_id:
            glDeleteTextures(1, [self.texture_id])
            self.texture_id = 0
            self.loaded = False


class TextureManager:
    """Manages multiple textures to avoid duplicates"""
    
    def __init__(self):
        """Initialize the texture manager"""
        self.logger = logging.getLogger("kitelyview.renderer.texture_manager")
        
        # Texture cache
        self.textures = {}  # Key: texture_id, Value: Texture object
        self.texture_paths = {}  # Key: path, Value: texture_id
        self.texture_memory = {}  # Key: hash of data, Value: texture_id
        
        # Default texture ID
        self.default_texture_id = None
        
        # Create default texture
        self._create_default_texture()
        
        self.logger.info("Texture manager initialized")
        
    def _create_default_texture(self):
        """Create a default texture for when textures fail to load"""
        texture = Texture()
        if texture.create_default_texture():
            self.default_texture_id = texture.texture_id
            self.textures[texture.texture_id] = texture
            self.logger.debug("Created default texture")
            
    def get_texture(self, texture_id):
        """Get a texture by ID"""
        return self.textures.get(texture_id, self.textures.get(self.default_texture_id))
        
    def load_texture(self, file_path):
        """Load a texture from file, reusing if already loaded"""
        # Check if already loaded
        if file_path in self.texture_paths:
            return self.texture_paths[file_path]
            
        # Create new texture
        texture = Texture()
        
        # Load texture data
        if texture.load_from_file(file_path):
            # Store in cache
            self.textures[texture.texture_id] = texture
            self.texture_paths[file_path] = texture.texture_id
            return texture.texture_id
        else:
            # Failed to load, return default texture
            return self.default_texture_id
            
    def load_texture_from_memory(self, data, width, height, channels=4):
        """Load a texture from memory data, reusing if already loaded"""
        # Generate a hash of the data to check for duplicates
        import hashlib
        data_hash = hashlib.md5(data).hexdigest()
        
        # Check if already loaded
        if data_hash in self.texture_memory:
            return self.texture_memory[data_hash]
            
        # Create new texture
        texture = Texture()
        
        # Load texture data
        if texture.load_from_memory(data, width, height, channels):
            # Store in cache
            self.textures[texture.texture_id] = texture
            self.texture_memory[data_hash] = texture.texture_id
            return texture.texture_id
        else:
            # Failed to load, return default texture
            return self.default_texture_id
            
    def load_texture_from_j2k(self, j2k_data):
        """Load a texture from JPEG2000 data, reusing if already loaded"""
        # Generate a hash of the data to check for duplicates
        import hashlib
        data_hash = hashlib.md5(j2k_data).hexdigest()
        
        # Check if already loaded
        if data_hash in self.texture_memory:
            return self.texture_memory[data_hash]
            
        # Create new texture
        texture = Texture()
        
        # Load texture data
        if texture.load_from_j2k(j2k_data):
            # Store in cache
            self.textures[texture.texture_id] = texture
            self.texture_memory[data_hash] = texture.texture_id
            return texture.texture_id
        else:
            # Failed to load, return default texture
            return self.default_texture_id
            
    def create_color_texture(self, r, g, b, a=1.0):
        """Create a solid color texture, reusing if already created"""
        # Create a key for this color
        color_key = f"color_{r}_{g}_{b}_{a}"
        
        # Check if already loaded
        if color_key in self.texture_memory:
            return self.texture_memory[color_key]
            
        # Create new texture
        texture = Texture()
        
        # Create color texture
        if texture.create_color_texture(r, g, b, a):
            # Store in cache
            self.textures[texture.texture_id] = texture
            self.texture_memory[color_key] = texture.texture_id
            return texture.texture_id
        else:
            # Failed to create, return default texture
            return self.default_texture_id
            
    def bind_texture(self, texture_id, texture_unit=GL_TEXTURE0):
        """Bind a texture to a texture unit"""
        texture = self.get_texture(texture_id)
        if texture:
            texture.bind(texture_unit)
            return True
        return False
        
    def cleanup(self):
        """Clean up all textures"""
        for texture in self.textures.values():
            texture.cleanup()
            
        self.textures.clear()
        self.texture_paths.clear()
        self.texture_memory.clear()
        self.default_texture_id = None
        
        self.logger.info("Texture manager cleaned up")
