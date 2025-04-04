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
    // Ambient lighting
    float ambientStrength = 0.3;
    vec3 ambient = ambientStrength * vec3(1.0, 1.0, 1.0);
    
    // Diffuse lighting
    vec3 normal = normalize(fragmentNormal);
    vec3 lightDir = normalize(lightPosition - fragmentPosition);
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = diff * vec3(1.0, 1.0, 1.0);
    
    // Specular lighting
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPosition - fragmentPosition);
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
    vec3 specular = specularStrength * spec * vec3(1.0, 1.0, 1.0);
    
    // Get base color (from texture or object color)
    vec4 baseColor;
    if (useTexture) {
        baseColor = texture2D(textureSampler, fragmentTexCoord);
    } else {
        baseColor = objectColor;
    }
    
    // Combine lighting components
    vec3 result = (ambient + diffuse + specular) * vec3(baseColor);
    
    // Set final color with original alpha
    gl_FragColor = vec4(result, baseColor.a);
}
