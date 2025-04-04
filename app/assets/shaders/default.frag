#version 330 core

in vec3 vertexNormal;
in vec3 fragPos;
in vec2 texCoordinates;

out vec4 fragColor;

uniform vec3 lightPosition;
uniform vec3 viewPosition;
uniform vec3 lightColor;
uniform vec3 objectColor;
uniform sampler2D textureSampler;
uniform int useTexture;

void main()
{
    // Ambient lighting
    float ambientStrength = 0.2;
    vec3 ambient = ambientStrength * lightColor;
    
    // Diffuse lighting
    vec3 norm = normalize(vertexNormal);
    vec3 lightDir = normalize(lightPosition - fragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    // Specular lighting
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPosition - fragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * lightColor;
    
    // Texture or color
    vec3 baseColor;
    if (useTexture > 0) {
        baseColor = texture(textureSampler, texCoordinates).rgb;
    } else {
        baseColor = objectColor;
    }
    
    // Final color
    vec3 result = (ambient + diffuse + specular) * baseColor;
    fragColor = vec4(result, 1.0);
}
