"""
Inventory models for KitelyView.
Represents the user's inventory items and folders.
"""

import logging
import uuid
import time

class InventoryFolder:
    """Represents a folder in the user's inventory"""
    
    def __init__(self, folder_id=None, name="New Folder", parent_id=None):
        """Initialize the inventory folder"""
        self.logger = logging.getLogger("kitelyview.models.inventory_folder")
        
        # Folder identification
        self.folder_id = folder_id or str(uuid.uuid4())
        self.parent_id = parent_id
        self.name = name
        
        # Folder content
        self.folders = {}  # Key: folder_id, Value: InventoryFolder
        self.items = {}    # Key: item_id, Value: InventoryItem
        
        # Folder metadata
        self.version = 1
        self.type_default = -1  # Default folder type
        self.created = int(time.time())
        self.owner_id = None
        
    def add_folder(self, folder):
        """Add a subfolder to this folder"""
        if isinstance(folder, InventoryFolder):
            folder.parent_id = self.folder_id
            self.folders[folder.folder_id] = folder
            return True
        return False
        
    def add_item(self, item):
        """Add an item to this folder"""
        if isinstance(item, InventoryItem):
            item.parent_id = self.folder_id
            self.items[item.item_id] = item
            return True
        return False
        
    def remove_folder(self, folder_id):
        """Remove a subfolder from this folder"""
        if folder_id in self.folders:
            del self.folders[folder_id]
            return True
        return False
        
    def remove_item(self, item_id):
        """Remove an item from this folder"""
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False
        
    def get_folder(self, folder_id):
        """Get a subfolder by ID"""
        return self.folders.get(folder_id)
        
    def get_item(self, item_id):
        """Get an item by ID"""
        return self.items.get(item_id)
        
    def get_folders(self):
        """Get all subfolders"""
        return list(self.folders.values())
        
    def get_items(self):
        """Get all items in this folder"""
        return list(self.items.values())
        
    def update_from_data(self, data):
        """Update folder from server data"""
        try:
            # Update identification
            if "folder_id" in data:
                self.folder_id = data["folder_id"]
                
            if "parent_id" in data:
                self.parent_id = data["parent_id"]
                
            if "name" in data:
                self.name = data["name"]
                
            # Update metadata
            if "version" in data:
                self.version = data["version"]
                
            if "type_default" in data:
                self.type_default = data["type_default"]
                
            if "created" in data:
                self.created = data["created"]
                
            if "owner_id" in data:
                self.owner_id = data["owner_id"]
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating folder from data: {e}", exc_info=True)
            return False
            
    def to_dict(self):
        """Convert folder to dictionary"""
        return {
            "folder_id": self.folder_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "version": self.version,
            "type_default": self.type_default,
            "created": self.created,
            "owner_id": self.owner_id,
            "folders": [folder.to_dict() for folder in self.folders.values()],
            "items": [item.to_dict() for item in self.items.values()]
        }


class InventoryItem:
    """Represents an item in the user's inventory"""
    
    # Item types
    TYPE_TEXTURE = 0
    TYPE_SOUND = 1
    TYPE_CALLING_CARD = 2
    TYPE_LANDMARK = 3
    TYPE_SCRIPT = 4
    TYPE_CLOTHING = 5
    TYPE_OBJECT = 6
    TYPE_NOTECARD = 7
    TYPE_CATEGORY = 8
    TYPE_ROOT = 9
    TYPE_LSL = 10
    TYPE_SNAPSHOT = 11
    TYPE_ATTACHMENT = 12
    TYPE_WEARABLE = 13
    TYPE_ANIMATION = 20
    TYPE_GESTURE = 21
    TYPE_MESH = 22
    
    # Inventory flags
    FLAG_NONE = 0
    FLAG_PROTECTED = 1
    FLAG_TEMPORARY = 2
    
    def __init__(self, item_id=None, name="New Item", item_type=TYPE_OBJECT):
        """Initialize the inventory item"""
        self.logger = logging.getLogger("kitelyview.models.inventory_item")
        
        # Item identification
        self.item_id = item_id or str(uuid.uuid4())
        self.parent_id = None
        self.name = name
        self.description = ""
        
        # Item data
        self.asset_id = None
        self.asset_type = item_type
        self.inventory_type = item_type
        self.flags = self.FLAG_NONE
        
        # Permissions
        self.creator_id = None
        self.owner_id = None
        self.last_owner_id = None
        self.group_id = None
        self.next_owner_perm = 0
        self.current_perm = 0
        self.group_perm = 0
        self.everyone_perm = 0
        self.base_perm = 0
        
        # Sale info
        self.sale_type = 0
        self.sale_price = 0
        
        # Metadata
        self.created = int(time.time())
        self.updated = int(time.time())
        
    def update_from_data(self, data):
        """Update item from server data"""
        try:
            # Update identification
            if "item_id" in data:
                self.item_id = data["item_id"]
                
            if "parent_id" in data:
                self.parent_id = data["parent_id"]
                
            if "name" in data:
                self.name = data["name"]
                
            if "description" in data:
                self.description = data["description"]
                
            # Update item data
            if "asset_id" in data:
                self.asset_id = data["asset_id"]
                
            if "asset_type" in data:
                self.asset_type = data["asset_type"]
                
            if "inventory_type" in data:
                self.inventory_type = data["inventory_type"]
                
            if "flags" in data:
                self.flags = data["flags"]
                
            # Update permissions
            if "creator_id" in data:
                self.creator_id = data["creator_id"]
                
            if "owner_id" in data:
                self.owner_id = data["owner_id"]
                
            if "last_owner_id" in data:
                self.last_owner_id = data["last_owner_id"]
                
            if "group_id" in data:
                self.group_id = data["group_id"]
                
            if "next_owner_perm" in data:
                self.next_owner_perm = data["next_owner_perm"]
                
            if "current_perm" in data:
                self.current_perm = data["current_perm"]
                
            if "group_perm" in data:
                self.group_perm = data["group_perm"]
                
            if "everyone_perm" in data:
                self.everyone_perm = data["everyone_perm"]
                
            if "base_perm" in data:
                self.base_perm = data["base_perm"]
                
            # Update sale info
            if "sale_type" in data:
                self.sale_type = data["sale_type"]
                
            if "sale_price" in data:
                self.sale_price = data["sale_price"]
                
            # Update metadata
            if "created" in data:
                self.created = data["created"]
                
            if "updated" in data:
                self.updated = data["updated"]
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating item from data: {e}", exc_info=True)
            return False
            
    def to_dict(self):
        """Convert item to dictionary"""
        return {
            "item_id": self.item_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "description": self.description,
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "inventory_type": self.inventory_type,
            "flags": self.flags,
            "creator_id": self.creator_id,
            "owner_id": self.owner_id,
            "last_owner_id": self.last_owner_id,
            "group_id": self.group_id,
            "next_owner_perm": self.next_owner_perm,
            "current_perm": self.current_perm,
            "group_perm": self.group_perm,
            "everyone_perm": self.everyone_perm,
            "base_perm": self.base_perm,
            "sale_type": self.sale_type,
            "sale_price": self.sale_price,
            "created": self.created,
            "updated": self.updated
        }
        
    def get_type_name(self):
        """Get the type name for this item"""
        type_names = {
            self.TYPE_TEXTURE: "Texture",
            self.TYPE_SOUND: "Sound",
            self.TYPE_CALLING_CARD: "Calling Card",
            self.TYPE_LANDMARK: "Landmark",
            self.TYPE_SCRIPT: "Script",
            self.TYPE_CLOTHING: "Clothing",
            self.TYPE_OBJECT: "Object",
            self.TYPE_NOTECARD: "Notecard",
            self.TYPE_CATEGORY: "Category",
            self.TYPE_ROOT: "Root",
            self.TYPE_LSL: "LSL Script",
            self.TYPE_SNAPSHOT: "Snapshot",
            self.TYPE_ATTACHMENT: "Attachment",
            self.TYPE_WEARABLE: "Wearable",
            self.TYPE_ANIMATION: "Animation",
            self.TYPE_GESTURE: "Gesture",
            self.TYPE_MESH: "Mesh"
        }
        return type_names.get(self.inventory_type, "Unknown")
        
    def is_copyable(self):
        """Check if item is copyable by the user"""
        return bool(self.current_perm & 0x00008000)
        
    def is_modifiable(self):
        """Check if item is modifiable by the user"""
        return bool(self.current_perm & 0x00004000)
        
    def is_transferable(self):
        """Check if item is transferable by the user"""
        return bool(self.current_perm & 0x00002000)
        
    def can_next_owner_copy(self):
        """Check if next owner can copy this item"""
        return bool(self.next_owner_perm & 0x00008000)
        
    def can_next_owner_modify(self):
        """Check if next owner can modify this item"""
        return bool(self.next_owner_perm & 0x00004000)
        
    def can_next_owner_transfer(self):
        """Check if next owner can transfer this item"""
        return bool(self.next_owner_perm & 0x00002000)
