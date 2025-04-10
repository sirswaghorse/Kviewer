/**
 * KitelyView - Building Manager
 * Handles object creation and editing UI
 */

class BuildingManager {
    constructor() {
        this.primTypeRadios = document.querySelectorAll('input[name="prim-type"]');
        this.objectSizeSlider = document.getElementById('object-size');
        this.objectColorPicker = document.getElementById('object-color');
        this.objectTransparencySlider = document.getElementById('object-transparency');
        this.objectPhysicalCheckbox = document.getElementById('object-physical');
        this.objectPhantomCheckbox = document.getElementById('object-phantom');
        this.objectTemporaryCheckbox = document.getElementById('object-temporary');
        this.createObjectButton = document.getElementById('create-object');
        this.editObjectButton = document.getElementById('edit-object');
        this.deleteObjectButton = document.getElementById('delete-object');
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Object selection event
        document.addEventListener('objectSelected', (event) => {
            this.onObjectSelected(event.detail.object);
        });
        
        document.addEventListener('objectDeselected', () => {
            this.resetControls();
        });
    }
    
    onObjectSelected(object) {
        // Update the UI controls to match the selected object
        if (!object || !object.userData) return;
        
        // Set size (assuming uniform scaling)
        this.objectSizeSlider.value = object.scale.x;
        
        // Set color
        const color = new THREE.Color();
        color.copy(object.material.color);
        this.objectColorPicker.value = '#' + color.getHexString();
        
        // Set transparency
        this.objectTransparencySlider.value = object.material.transparent ? 1 - object.material.opacity : 0;
        
        // Set physics flags
        this.objectPhysicalCheckbox.checked = object.userData.isPhysical || false;
        this.objectPhantomCheckbox.checked = object.userData.isPhantom || false;
        this.objectTemporaryCheckbox.checked = object.userData.isTemporary || false;
        
        // Enable edit and delete buttons
        this.editObjectButton.disabled = false;
        this.deleteObjectButton.disabled = false;
    }
    
    resetControls() {
        // Reset controls to default state
        this.objectSizeSlider.value = 1.0;
        this.objectColorPicker.value = '#f44336';
        this.objectTransparencySlider.value = 0;
        this.objectPhysicalCheckbox.checked = false;
        this.objectPhantomCheckbox.checked = false;
        this.objectTemporaryCheckbox.checked = false;
        
        // Disable edit and delete buttons
        this.editObjectButton.disabled = true;
        this.deleteObjectButton.disabled = true;
    }
}

// Initialize building manager when DOM is loaded
let buildingManager;
document.addEventListener('DOMContentLoaded', () => {
    buildingManager = new BuildingManager();
});