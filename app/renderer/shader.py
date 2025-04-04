"""
Shader program implementation for OpenGL rendering.
Handles compilation and usage of GLSL shaders.
"""

import logging
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

class ShaderProgram:
    """OpenGL shader program wrapper"""
    
    def __init__(self):
        """Initialize shader program"""
        self.logger = logging.getLogger("kitelyview.renderer.shader")
        self.program_id = 0
        self.vertex_shader = None
        self.fragment_shader = None
        self.uniforms = {}
        
    def load_from_strings(self, vertex_src, fragment_src):
        """Create shader program from source strings"""
        try:
            self.vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)
            self.fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)
            self.logger.info("Shader compilation successful")
        except Exception as e:
            self.logger.error(f"Shader compilation error: {e}")
            raise
            
    def load_from_files(self, vertex_file, fragment_file):
        """Create shader program from source files"""
        try:
            # Read vertex shader
            with open(vertex_file, 'r') as file:
                vertex_src = file.read()
                
            # Read fragment shader
            with open(fragment_file, 'r') as file:
                fragment_src = file.read()
                
            # Load from strings
            self.load_from_strings(vertex_src, fragment_src)
            
            self.logger.info(f"Loaded shaders from {vertex_file} and {fragment_file}")
        except Exception as e:
            self.logger.error(f"Error loading shader files: {e}")
            raise
            
    def link(self):
        """Link shader program"""
        if not self.vertex_shader or not self.fragment_shader:
            self.logger.error("Cannot link program, shaders not compiled")
            return False
            
        try:
            self.program_id = compileProgram(self.vertex_shader, self.fragment_shader)
            self.logger.info(f"Shader program linked successfully, ID: {self.program_id}")
            return True
        except Exception as e:
            self.logger.error(f"Shader program link error: {e}")
            return False
            
    def use(self):
        """Activate shader program"""
        if self.program_id:
            glUseProgram(self.program_id)
        else:
            self.logger.warning("Attempted to use unlinked shader program")
            
    def get_uniform_location(self, name):
        """Get the location of a uniform variable"""
        if name in self.uniforms:
            return self.uniforms[name]
            
        if not self.program_id:
            self.logger.warning(f"Cannot get uniform {name}, program not linked")
            return -1
            
        location = glGetUniformLocation(self.program_id, name)
        if location == -1:
            self.logger.warning(f"Uniform '{name}' not found in shader program")
        else:
            self.uniforms[name] = location
            
        return location
        
    def set_uniform_1f(self, name, value):
        """Set float uniform"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform1f(location, value)
            
    def set_uniform_2f(self, name, x, y):
        """Set vec2 uniform"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform2f(location, x, y)
            
    def set_uniform_3f(self, name, x, y, z):
        """Set vec3 uniform"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform3f(location, x, y, z)
            
    def set_uniform_4f(self, name, x, y, z, w):
        """Set vec4 uniform"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform4f(location, x, y, z, w)
            
    def set_uniform_1i(self, name, value):
        """Set int uniform"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform1i(location, value)
            
    def set_uniform_matrix4fv(self, name, matrix):
        """Set 4x4 matrix uniform"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniformMatrix4fv(location, 1, GL_FALSE, matrix)
            
    def cleanup(self):
        """Clean up shader resources"""
        if self.program_id:
            glDeleteProgram(self.program_id)
            self.program_id = 0