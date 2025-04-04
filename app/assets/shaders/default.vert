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
    
    // Calculate fragment position in world space
    fragmentPosition = vec3(model * vec4(position, 1.0));
    
    // Calculate normal in world space
    // The normal matrix is the transpose of the inverse of the model matrix
    fragmentNormal = mat3(transpose(inverse(model))) * normal;
    
    // Pass texture coordinates to fragment shader
    fragmentTexCoord = texCoord;
}
