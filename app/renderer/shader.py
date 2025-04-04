"""
Shader implementation for the 3D renderer.
Handles loading, compiling, and using GLSL shaders.
"""

import logging
import os
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

class Shader:
    """Wrapper for a single GLSL shader"""
    
    def __init__(self, shader_type, file_path=None, source=None):
        """Initialize the shader"""
        self.logger = logging.getLogger("kitelyview.renderer.shader")
        
        self.shader_type = shader_type
        self.shader_id = None
        
        # Load shader source
        if file_path:
            self.source = self._load_shader_source(file_path)
        elif source:
            self.source = source
        else:
            raise ValueError("Either file_path or source must be provided")
            
        # Compile shader
        self._compile()
        
    def _load_shader_source(self, file_path):
        """Load shader source code from file"""
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Failed to load shader from {file_path}: {e}")
            
            # Provide a default shader if file can't be loaded
            if self.shader_type == GL_VERTEX_SHADER:
                return self._get_default_vertex_shader()
            elif self.shader_type == GL_FRAGMENT_SHADER:
                return self._get_default_fragment_shader()
            else:
                raise
                
    def _get_default_vertex_shader(self):
        """Return a default vertex shader"""
        self.logger.warning("Using default vertex shader")
        return """
        #version 120
        
        // Input vertex data
        attribute vec3 position;
        attribute vec3 normal;
        attribute vec2 texCoord;
        
        // Output data to fragment shader
        varying vec3 fragmentNormal;
        varying vec2 fragmentTexCoord;
        varying vec3 fragmentPosition;
        
        // Uniforms
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        
        void main() {
            // Calculate position
            gl_Position = projection * view * model * vec4(position, 1.0);
            
            // Pass data to fragment shader
            fragmentPosition = vec3(model * vec4(position, 1.0));
            fragmentNormal = mat3(transpose(inverse(model))) * normal;
            fragmentTexCoord = texCoord;
        }
        """
        
    def _get_default_fragment_shader(self):
        """Return a default fragment shader"""
        self.logger.warning("Using default fragment shader")
        return """
        #version 120
        
        // Input data from vertex shader
        varying vec3 fragmentNormal;
        varying vec2 fragmentTexCoord;
        varying vec3 fragmentPosition;
        
        // Uniforms
        uniform vec3 lightPosition;
        uniform vec3 viewPosition;
        uniform vec4 objectColor;
        uniform sampler2D textureSampler;
        uniform bool useTexture;
        
        void main() {
            // Normalize normal
            vec3 normal = normalize(fragmentNormal);
            
            // Ambient
            float ambientStrength = 0.3;
            vec3 ambient = ambientStrength * vec3(1.0, 1.0, 1.0);
            
            // Diffuse
            vec3 lightDir = normalize(lightPosition - fragmentPosition);
            float diff = max(dot(normal, lightDir), 0.0);
            vec3 diffuse = diff * vec3(1.0, 1.0, 1.0);
            
            // Base color
            vec4 baseColor = objectColor;
            if (useTexture) {
                baseColor = texture2D(textureSampler, fragmentTexCoord);
            }
            
            // Combine colors
            vec3 result = (ambient + diffuse) * vec3(baseColor);
            gl_FragColor = vec4(result, baseColor.a);
        }
        """
        
    def _compile(self):
        """Compile the shader"""
        try:
            self.shader_id = compileShader(self.source, self.shader_type)
            self.logger.debug(f"Compiled shader of type {self.shader_type}")
        except Exception as e:
            self.logger.error(f"Failed to compile shader: {e}")
            raise
            
    def get_id(self):
        """Get the shader ID"""
        return self.shader_id
        
    def cleanup(self):
        """Clean up resources"""
        if self.shader_id:
            glDeleteShader(self.shader_id)
            self.shader_id = None

class ShaderProgram:
    """Wrapper for a GLSL shader program"""
    
    def __init__(self, shaders):
        """Initialize the shader program"""
        self.logger = logging.getLogger("kitelyview.renderer.shader_program")
        
        self.program_id = None
        self.shaders = shaders
        
        # Create program
        self._create_program()
        
    def _create_program(self):
        """Create the shader program"""
        try:
            shader_ids = [shader.get_id() for shader in self.shaders]
            self.program_id = glCreateProgram()
            
            # Attach shaders
            for shader_id in shader_ids:
                glAttachShader(self.program_id, shader_id)
                
            # Link program
            glLinkProgram(self.program_id)
            
            # Check for link errors
            status = glGetProgramiv(self.program_id, GL_LINK_STATUS)
            if status == GL_FALSE:
                log = glGetProgramInfoLog(self.program_id)
                self.logger.error(f"Failed to link shader program: {log}")
                glDeleteProgram(self.program_id)
                self.program_id = None
                raise RuntimeError(f"Shader program linkage failed: {log}")
                
            self.logger.debug("Shader program linked successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create shader program: {e}")
            if self.program_id:
                glDeleteProgram(self.program_id)
                self.program_id = None
            raise
            
    def use(self):
        """Use this shader program"""
        if self.program_id:
            glUseProgram(self.program_id)
            
    def unuse(self):
        """Stop using this shader program"""
        glUseProgram(0)
        
    def get_uniform_location(self, name):
        """Get the location of a uniform variable"""
        if not self.program_id:
            return -1
        return glGetUniformLocation(self.program_id, name)
        
    def get_attribute_location(self, name):
        """Get the location of an attribute variable"""
        if not self.program_id:
            return -1
        return glGetAttribLocation(self.program_id, name)
        
    def set_uniform_1f(self, name, value):
        """Set a float uniform value"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform1f(location, value)
            
    def set_uniform_2f(self, name, x, y):
        """Set a vec2 uniform value"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform2f(location, x, y)
            
    def set_uniform_3f(self, name, x, y, z):
        """Set a vec3 uniform value"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform3f(location, x, y, z)
            
    def set_uniform_4f(self, name, x, y, z, w):
        """Set a vec4 uniform value"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform4f(location, x, y, z, w)
            
    def set_uniform_1i(self, name, value):
        """Set an int uniform value"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform1i(location, value)
            
    def set_uniform_matrix4fv(self, name, matrix_data):
        """Set a mat4 uniform value"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniformMatrix4fv(location, 1, GL_FALSE, matrix_data)
            
    def set_uniform_1fv(self, name, data):
        """Set a float array uniform value"""
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform1fv(location, len(data), data)
            
    def cleanup(self):
        """Clean up resources"""
        if self.program_id:
            glDeleteProgram(self.program_id)
            self.program_id = None
