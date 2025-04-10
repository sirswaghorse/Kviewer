/**
 * KitelyView - Object Manager
 * Handles creation and manipulation of in-world objects
 */

class ObjectManager {
    constructor(sceneManager) {
        this.sceneManager = sceneManager;
        this.objects = [];
        this.nextObjectId = 1;
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Listen for create object button click
        document.getElementById('create-object').addEventListener('click', () => {
            this.createObjectFromUI();
        });
        
        // Listen for edit object button click
        document.getElementById('edit-object').addEventListener('click', () => {
            this.editSelectedObject();
        });
        
        // Listen for delete object button click
        document.getElementById('delete-object').addEventListener('click', () => {
            this.deleteSelectedObject();
        });
    }
    
    createObjectFromUI() {
        // Get object properties from UI
        const type = document.querySelector('input[name="prim-type"]:checked').value;
        const size = parseFloat(document.getElementById('object-size').value);
        const color = document.getElementById('object-color').value;
        const transparency = parseFloat(document.getElementById('object-transparency').value);
        const isPhysical = document.getElementById('object-physical').checked;
        const isPhantom = document.getElementById('object-phantom').checked;
        const isTemporary = document.getElementById('object-temporary').checked;
        
        // Create the object
        const objectData = {
            id: this.nextObjectId++,
            type: type,
            position: { x: 0, y: size / 2, z: 0 },
            rotation: { x: 0, y: 0, z: 0 },
            scale: { x: size, y: size, z: size },
            color: color,
            transparency: transparency,
            isPhysical: isPhysical,
            isPhantom: isPhantom,
            isTemporary: isTemporary
        };
        
        const object = this.createObject(objectData);
        if (object) {
            this.objects.push(objectData);
            
            // Add log entry
            addLogEntry(`Created ${type} object with ID: ${objectData.id}`, 'info');
        }
    }
    
    createObject(objectData) {
        let geometry;
        
        // Create geometry based on type
        switch (objectData.type) {
            case 'box':
                geometry = new THREE.BoxGeometry(1, 1, 1);
                break;
            case 'sphere':
                geometry = new THREE.SphereGeometry(0.5, 32, 32);
                break;
            case 'cylinder':
                geometry = new THREE.CylinderGeometry(0.5, 0.5, 1, 32);
                break;
            case 'prism':
                geometry = new THREE.ConeGeometry(0.5, 1, 4);
                break;
            case 'torus':
                geometry = new THREE.TorusGeometry(0.5, 0.2, 16, 32);
                break;
            default:
                geometry = new THREE.BoxGeometry(1, 1, 1);
        }
        
        // Create material
        const material = new THREE.MeshStandardMaterial({
            color: new THREE.Color(objectData.color),
            transparent: objectData.transparency > 0,
            opacity: 1 - objectData.transparency,
            roughness: 0.7,
            metalness: 0.3
        });
        
        // Create mesh
        const object = new THREE.Mesh(geometry, material);
        
        // Set position, rotation, and scale
        object.position.set(
            objectData.position.x,
            objectData.position.y,
            objectData.position.z
        );
        
        object.rotation.set(
            objectData.rotation.x,
            objectData.rotation.y,
            objectData.rotation.z
        );
        
        object.scale.set(
            objectData.scale.x,
            objectData.scale.y,
            objectData.scale.z
        );
        
        // Set shadow properties
        object.castShadow = true;
        object.receiveShadow = true;
        
        // Store data reference
        object.userData = {
            id: objectData.id,
            isPhysical: objectData.isPhysical,
            isPhantom: objectData.isPhantom,
            isTemporary: objectData.isTemporary
        };
        
        // Add to scene
        this.sceneManager.addObject(object);
        
        return object;
    }
    
    editSelectedObject() {
        if (!this.sceneManager.selectedObject) return;
        
        // Get the selected object
        const object = this.sceneManager.selectedObject;
        const objectId = object.userData.id;
        
        // Find the corresponding data
        const objectDataIndex = this.objects.findIndex(o => o.id === objectId);
        if (objectDataIndex === -1) return;
        
        // Get updated values from UI
        const size = parseFloat(document.getElementById('object-size').value);
        const color = document.getElementById('object-color').value;
        const transparency = parseFloat(document.getElementById('object-transparency').value);
        const isPhysical = document.getElementById('object-physical').checked;
        const isPhantom = document.getElementById('object-phantom').checked;
        const isTemporary = document.getElementById('object-temporary').checked;
        
        // Update object appearance
        object.scale.set(size, size, size);
        object.material.color.set(color);
        object.material.transparent = transparency > 0;
        object.material.opacity = 1 - transparency;
        
        // Update object properties
        object.userData.isPhysical = isPhysical;
        object.userData.isPhantom = isPhantom;
        object.userData.isTemporary = isTemporary;
        
        // Update data store
        this.objects[objectDataIndex].scale = { x: size, y: size, z: size };
        this.objects[objectDataIndex].color = color;
        this.objects[objectDataIndex].transparency = transparency;
        this.objects[objectDataIndex].isPhysical = isPhysical;
        this.objects[objectDataIndex].isPhantom = isPhantom;
        this.objects[objectDataIndex].isTemporary = isTemporary;
        
        // Add log entry
        addLogEntry(`Updated object with ID: ${objectId}`, 'info');
    }
    
    deleteSelectedObject() {
        if (!this.sceneManager.selectedObject) return;
        
        // Get the selected object
        const object = this.sceneManager.selectedObject;
        const objectId = object.userData.id;
        
        // Remove from scene
        this.sceneManager.removeObject(object);
        
        // Remove from data store
        const objectIndex = this.objects.findIndex(o => o.id === objectId);
        if (objectIndex !== -1) {
            this.objects.splice(objectIndex, 1);
        }
        
        // Add log entry
        addLogEntry(`Deleted object with ID: ${objectId}`, 'info');
    }
    
    getObjectById(id) {
        return this.objects.find(o => o.id === id);
    }
    
    loadObjectFromInventory(inventoryItem) {
        // Create object data from inventory item
        const objectData = {
            id: this.nextObjectId++,
            type: this.getTypeFromItem(inventoryItem),
            position: { x: 0, y: 1, z: 0 },
            rotation: { x: 0, y: 0, z: 0 },
            scale: { x: 1, y: 1, z: 1 },
            color: '#' + Math.floor(Math.random() * 16777215).toString(16),
            transparency: 0,
            isPhysical: false,
            isPhantom: false,
            isTemporary: false
        };
        
        const object = this.createObject(objectData);
        if (object) {
            this.objects.push(objectData);
            
            // Add log entry
            addLogEntry(`Created object from inventory item: ${inventoryItem.name}`, 'info');
        }
    }
    
    getTypeFromItem(inventoryItem) {
        // Map inventory item type to object type
        switch (inventoryItem.type) {
            case 'mesh':
                return 'mesh';
            case 'texture':
                return 'box';
            case 'object':
                return 'box';
            default:
                return 'box';
        }
    }
}

// Helper function to add log entries
function addLogEntry(message, level) {
    const systemLog = document.getElementById('system-log');
    if (!systemLog) return;
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${level}`;
    logEntry.textContent = message;
    
    systemLog.appendChild(logEntry);
    
    // Auto-scroll to bottom
    systemLog.scrollTop = systemLog.scrollHeight;
}

// Initialize object manager after scene is created
let objectManager;
document.addEventListener('DOMContentLoaded', () => {
    // Wait for scene manager to be initialized
    setTimeout(() => {
        if (sceneManager) {
            objectManager = new ObjectManager(sceneManager);
        }
    }, 300);
});