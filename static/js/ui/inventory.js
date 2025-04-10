/**
 * KitelyView - Inventory Manager
 * Handles the inventory system with drag and drop functionality
 */

class InventoryManager {
    constructor() {
        this.currentFolder = 'root';
        this.folders = {
            'root': {
                name: 'My Inventory',
                items: []
            }
        };
        
        // Initialize demo inventory items
        this.initializeDemoInventory();
        
        // Initialize event listeners
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Create folder button
        document.getElementById('create-folder').addEventListener('click', () => {
            this.createNewFolder();
        });
        
        // Folder dropdown change
        document.getElementById('folder-dropdown').addEventListener('change', (event) => {
            this.switchFolder(event.target.value);
        });
        
        // Initialize drag-and-drop for the 3D scene
        this.initDragAndDrop();
    }
    
    initializeDemoInventory() {
        // Add some demo folders
        this.addFolder('clothing', 'Clothing');
        this.addFolder('objects', 'Objects');
        this.addFolder('textures', 'Textures');
        
        // Add demo items to folders
        this.addItem('root', { id: 1, name: 'Box', type: 'object', description: 'A simple box' });
        this.addItem('root', { id: 2, name: 'Sphere', type: 'object', description: 'A simple sphere' });
        
        this.addItem('clothing', { id: 3, name: 'Blue Shirt', type: 'clothing', description: 'A blue shirt' });
        this.addItem('clothing', { id: 4, name: 'Black Pants', type: 'clothing', description: 'Black pants' });
        
        this.addItem('objects', { id: 5, name: 'Chair', type: 'object', description: 'A wooden chair' });
        this.addItem('objects', { id: 6, name: 'Table', type: 'object', description: 'A wooden table' });
        
        this.addItem('textures', { id: 7, name: 'Wood', type: 'texture', description: 'Wood texture' });
        this.addItem('textures', { id: 8, name: 'Metal', type: 'texture', description: 'Metal texture' });
        
        // Render initial inventory view
        this.renderInventory();
        this.updateFolderDropdown();
    }
    
    addFolder(id, name) {
        this.folders[id] = {
            name: name,
            items: []
        };
    }
    
    addItem(folderId, item) {
        if (this.folders[folderId]) {
            this.folders[folderId].items.push(item);
        }
    }
    
    createNewFolder() {
        const folderName = prompt('Enter folder name:');
        if (folderName && folderName.trim() !== '') {
            const folderId = 'folder_' + Date.now();
            this.addFolder(folderId, folderName);
            this.updateFolderDropdown();
            
            // Add log entry
            addLogEntry(`Created new folder: ${folderName}`, 'info');
        }
    }
    
    switchFolder(folderId) {
        if (this.folders[folderId]) {
            this.currentFolder = folderId;
            this.renderInventory();
        }
    }
    
    renderInventory() {
        const inventoryContainer = document.getElementById('inventory-items');
        inventoryContainer.innerHTML = '';
        
        // Add navigation to parent folder if not in root
        if (this.currentFolder !== 'root') {
            const backItem = document.createElement('div');
            backItem.className = 'inventory-folder';
            backItem.innerHTML = '<div class="inventory-icon">⬆️</div> ..';
            backItem.addEventListener('click', () => {
                this.switchFolder('root');
            });
            inventoryContainer.appendChild(backItem);
        }
        
        // Add subfolders first
        for (const folderId in this.folders) {
            if (folderId !== 'root' && folderId !== this.currentFolder) {
                const folderElement = document.createElement('div');
                folderElement.className = 'inventory-folder';
                folderElement.innerHTML = `<div class="inventory-icon">📁</div> ${this.folders[folderId].name}`;
                folderElement.addEventListener('click', () => {
                    this.switchFolder(folderId);
                });
                inventoryContainer.appendChild(folderElement);
            }
        }
        
        // Add items in current folder
        if (this.folders[this.currentFolder]) {
            this.folders[this.currentFolder].items.forEach(item => {
                const itemElement = document.createElement('div');
                itemElement.className = 'inventory-item';
                itemElement.draggable = true;
                itemElement.dataset.itemId = item.id;
                itemElement.dataset.itemType = item.type;
                
                // Choose icon based on item type
                let icon = '🔍';
                switch (item.type) {
                    case 'object':
                        icon = '📦';
                        break;
                    case 'clothing':
                        icon = '👕';
                        break;
                    case 'texture':
                        icon = '🖼️';
                        break;
                    case 'animation':
                        icon = '🎭';
                        break;
                    case 'script':
                        icon = '📝';
                        break;
                }
                
                itemElement.innerHTML = `<div class="inventory-icon">${icon}</div> ${item.name}`;
                
                // Add drag event listeners
                this.addDragEventListeners(itemElement, item);
                
                inventoryContainer.appendChild(itemElement);
            });
        }
    }
    
    updateFolderDropdown() {
        const dropdown = document.getElementById('folder-dropdown');
        dropdown.innerHTML = '';
        
        // Add all folders to dropdown
        for (const folderId in this.folders) {
            const option = document.createElement('option');
            option.value = folderId;
            option.textContent = this.folders[folderId].name;
            
            if (folderId === this.currentFolder) {
                option.selected = true;
            }
            
            dropdown.appendChild(option);
        }
    }
    
    addDragEventListeners(element, item) {
        element.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('application/json', JSON.stringify(item));
            e.dataTransfer.setData('text/plain', item.name);
            element.classList.add('dragging');
        });
        
        element.addEventListener('dragend', () => {
            element.classList.remove('dragging');
        });
    }
    
    initDragAndDrop() {
        const sceneElement = document.getElementById('3d-scene');
        
        // Listen for drag over events
        sceneElement.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
        });
        
        // Listen for drop events
        sceneElement.addEventListener('drop', (e) => {
            e.preventDefault();
            
            try {
                // Get the dragged item data
                const itemJson = e.dataTransfer.getData('application/json');
                if (!itemJson) return;
                
                const item = JSON.parse(itemJson);
                
                // Handle the dropped item based on type
                if (item.type === 'object' || item.type === 'texture') {
                    this.handleObjectDrop(item, e);
                } else if (item.type === 'clothing') {
                    this.handleClothingDrop(item);
                }
            } catch (error) {
                console.error('Error handling drop:', error);
            }
        });
    }
    
    handleObjectDrop(item, event) {
        // Only proceed if we have initialized the object manager
        if (!objectManager) return;
        
        // Create an object from the inventory item
        objectManager.loadObjectFromInventory(item);
        
        // Add log entry
        addLogEntry(`Placed ${item.name} from inventory`, 'info');
    }
    
    handleClothingDrop(item) {
        // Only proceed if we have initialized the avatar manager
        if (!avatarManager) return;
        
        // Apply clothing to avatar
        // This is a simplified example - in a real app, we would load the actual clothing model/texture
        const appearance = {
            outfitStyle: 'casual',
            outfitPrimaryColor: '#' + Math.floor(Math.random() * 16777215).toString(16),
            outfitSecondaryColor: '#' + Math.floor(Math.random() * 16777215).toString(16)
        };
        
        avatarManager.updateAppearance(appearance);
        
        // Add log entry
        addLogEntry(`Wearing ${item.name} from inventory`, 'info');
    }
    
    getItemById(id) {
        // Search through all folders for the item
        for (const folderId in this.folders) {
            const folder = this.folders[folderId];
            const item = folder.items.find(item => item.id === id);
            if (item) return item;
        }
        return null;
    }
}

// Initialize inventory manager when DOM is loaded
let inventoryManager;
document.addEventListener('DOMContentLoaded', () => {
    inventoryManager = new InventoryManager();
});