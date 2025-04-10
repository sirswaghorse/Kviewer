/**
 * KitelyView - 3D Scene Manager
 * Handles the Three.js scene setup and rendering
 */

class SceneManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.objects = [];
        this.selectedObject = null;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        this.init();
    }
    
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x87ceeb); // Sky blue
        
        // Create camera
        this.camera = new THREE.PerspectiveCamera(75, this.container.clientWidth / this.container.clientHeight, 0.1, 1000);
        this.camera.position.set(0, 2, 5);
        
        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);
        
        // Create orbit controls
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        
        // Add lights
        this.addLights();
        
        // Add grid for visual reference
        this.addGrid();
        
        // Add event listeners
        window.addEventListener('resize', () => this.onWindowResize());
        this.renderer.domElement.addEventListener('mousedown', (event) => this.onMouseDown(event));
        
        // Start animation loop
        this.animate();
    }
    
    addLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);
        
        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(-10, 20, 10);
        directionalLight.castShadow = true;
        directionalLight.shadow.camera.near = 0.1;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.left = -20;
        directionalLight.shadow.camera.right = 20;
        directionalLight.shadow.camera.top = 20;
        directionalLight.shadow.camera.bottom = -20;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
    }
    
    addGrid() {
        const gridHelper = new THREE.GridHelper(100, 100, 0x888888, 0xcccccc);
        this.scene.add(gridHelper);
    }
    
    onWindowResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }
    
    onMouseDown(event) {
        // Calculate mouse position in normalized device coordinates
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        // Update the picking ray with the camera and mouse position
        this.raycaster.setFromCamera(this.mouse, this.camera);
        
        // Calculate objects intersecting the picking ray
        const intersects = this.raycaster.intersectObjects(this.objects);
        
        if (intersects.length > 0) {
            // Select the first intersected object
            this.selectObject(intersects[0].object);
        } else {
            // Deselect if clicked on empty space
            this.deselectObject();
        }
    }
    
    selectObject(object) {
        if (this.selectedObject) {
            // Remove highlight from previously selected object
            this.selectedObject.material.emissive.setHex(this.selectedObject.currentHex);
        }
        
        this.selectedObject = object;
        this.selectedObject.currentHex = this.selectedObject.material.emissive.getHex();
        this.selectedObject.material.emissive.setHex(0x333333);
        
        // Enable edit and delete buttons
        document.getElementById('edit-object').disabled = false;
        document.getElementById('delete-object').disabled = false;
        
        // Dispatch custom event
        const event = new CustomEvent('objectSelected', { detail: { object: this.selectedObject } });
        document.dispatchEvent(event);
    }
    
    deselectObject() {
        if (this.selectedObject) {
            this.selectedObject.material.emissive.setHex(this.selectedObject.currentHex);
            this.selectedObject = null;
            
            // Disable edit and delete buttons
            document.getElementById('edit-object').disabled = true;
            document.getElementById('delete-object').disabled = true;
            
            // Dispatch custom event
            const event = new CustomEvent('objectDeselected');
            document.dispatchEvent(event);
        }
    }
    
    addObject(object) {
        this.scene.add(object);
        this.objects.push(object);
    }
    
    removeObject(object) {
        const index = this.objects.indexOf(object);
        if (index !== -1) {
            this.objects.splice(index, 1);
        }
        this.scene.remove(object);
        
        if (this.selectedObject === object) {
            this.selectedObject = null;
            document.getElementById('edit-object').disabled = true;
            document.getElementById('delete-object').disabled = true;
        }
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Update controls
        this.controls.update();
        
        // Render scene
        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize scene when DOM is loaded
let sceneManager;
document.addEventListener('DOMContentLoaded', () => {
    sceneManager = new SceneManager('3d-scene');
});