/**
 * KitelyView - Terrain Manager
 * Handles terrain generation and rendering
 */

class TerrainManager {
    constructor(sceneManager) {
        this.sceneManager = sceneManager;
        this.terrain = null;
        this.water = null;
        this.terrainSize = 100;
        this.resolution = 128;
        this.maxHeight = 10;
        this.waterLevel = 1;
        
        this.init();
    }
    
    init() {
        this.createTerrain();
        this.createWater();
    }
    
    createTerrain() {
        // Create terrain geometry
        const geometry = new THREE.PlaneGeometry(
            this.terrainSize, 
            this.terrainSize, 
            this.resolution - 1, 
            this.resolution - 1
        );
        
        // Rotate to horizontal plane
        geometry.rotateX(-Math.PI / 2);
        
        // Generate height map
        this.generateHeightMap(geometry);
        
        // Create material with grass texture
        const material = new THREE.MeshStandardMaterial({
            color: 0x8bc34a,
            flatShading: true,
            side: THREE.DoubleSide,
            roughness: 0.8,
            metalness: 0.1
        });
        
        // Create mesh
        this.terrain = new THREE.Mesh(geometry, material);
        this.terrain.receiveShadow = true;
        
        // Add to scene
        this.sceneManager.scene.add(this.terrain);
    }
    
    generateHeightMap(geometry) {
        // Create a simple procedural height map
        const simplex = new SimplexNoise();
        const vertices = geometry.attributes.position.array;
        
        for (let i = 0; i < vertices.length; i += 3) {
            // Get x and z coordinates
            const x = vertices[i];
            const z = vertices[i + 2];
            
            // Generate height with multiple octaves of noise
            let height = 0;
            
            // Large features
            height += simplex.noise2D(x * 0.01, z * 0.01) * 0.6;
            
            // Medium features
            height += simplex.noise2D(x * 0.04, z * 0.04) * 0.3;
            
            // Small features
            height += simplex.noise2D(x * 0.1, z * 0.1) * 0.1;
            
            // Scale height and set y-coordinate
            vertices[i + 1] = height * this.maxHeight;
        }
        
        // Update geometry
        geometry.computeVertexNormals();
        geometry.attributes.position.needsUpdate = true;
    }
    
    createWater() {
        // Create water plane
        const geometry = new THREE.PlaneGeometry(this.terrainSize * 2, this.terrainSize * 2);
        geometry.rotateX(-Math.PI / 2);
        
        // Create water material
        const material = new THREE.MeshStandardMaterial({
            color: 0x1e88e5,
            transparent: true,
            opacity: 0.8,
            side: THREE.DoubleSide,
            roughness: 0.1,
            metalness: 0.6
        });
        
        // Create mesh
        this.water = new THREE.Mesh(geometry, material);
        this.water.position.y = this.waterLevel;
        
        // Add to scene
        this.sceneManager.scene.add(this.water);
    }
    
    updateWaterLevel(level) {
        this.waterLevel = level;
        if (this.water) {
            this.water.position.y = level;
        }
    }
}

// SimplexNoise implementation
// Simplified version for this demo
class SimplexNoise {
    constructor() {}
    
    noise2D(x, y) {
        // Simple implementation of perlin-like noise for demo purposes
        const X = Math.floor(x) & 255;
        const Y = Math.floor(y) & 255;
        const xf = x - Math.floor(x);
        const yf = y - Math.floor(y);
        
        // Simple noise function
        const n = Math.sin(X * 0.3 + Y * 0.7) * Math.cos(X * 0.7 + Y * 0.3);
        
        return n;
    }
}

// Initialize terrain manager after scene is created
let terrainManager;
document.addEventListener('DOMContentLoaded', () => {
    // Wait for scene manager to be initialized
    setTimeout(() => {
        if (sceneManager) {
            terrainManager = new TerrainManager(sceneManager);
        }
    }, 200);
});