"""
Inventory panel for the KitelyView viewer using PyQt5.
Displays and manages the user's inventory items.
"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QMenu, QAction, QLabel, QComboBox, QLineEdit, QToolBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from app.models.inventory import InventoryFolder, InventoryItem

class InventoryPanel(QWidget):
    """Panel for displaying user inventory"""
    
    def __init__(self, parent):
        """Initialize the inventory panel"""
        super(InventoryPanel, self).__init__(parent)
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.inventory_panel")
        self.logger.info("Initializing inventory panel")
        
        # Store parent reference (MainWindow)
        self.main_window = parent
        
        # Create UI elements
        self._create_ui()
        
        # Initialize data
        self.root_folder = None
        
        self.logger.info("Inventory panel initialized")
        
    def _create_ui(self):
        """Create UI elements"""
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create toolbar
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search inventory...")
        toolbar.addWidget(self.search_input)
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Items", "Recent Items", "Worn Items"])
        toolbar.addWidget(self.filter_combo)
        
        # Add toolbar to layout
        main_layout.addWidget(toolbar)
        
        # Create tree widget for inventory
        self.inventory_tree = QTreeWidget()
        self.inventory_tree.setHeaderLabels(["Name", "Type"])
        self.inventory_tree.setColumnWidth(0, 180)
        self.inventory_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.inventory_tree.customContextMenuRequested.connect(self.show_context_menu)
        
        # Add tree to layout
        main_layout.addWidget(self.inventory_tree)
        
        # Create bottom buttons
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.create_button = QPushButton("New Folder")
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.create_button)
        
        # Add buttons to layout
        main_layout.addLayout(button_layout)
        
        # Set main layout
        self.setLayout(main_layout)
        
        # Connect signals
        self.refresh_button.clicked.connect(self.refresh_inventory)
        self.create_button.clicked.connect(self.create_new_folder)
        self.search_input.textChanged.connect(self.filter_inventory)
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        
    def show_context_menu(self, position):
        """Show context menu for inventory items"""
        # Get the tree item at the position
        item = self.inventory_tree.itemAt(position)
        if not item:
            return
            
        # Create context menu
        menu = QMenu()
        
        # Add actions
        open_action = QAction("Open", self)
        wear_action = QAction("Wear", self)
        properties_action = QAction("Properties", self)
        delete_action = QAction("Delete", self)
        
        # Add actions to menu
        menu.addAction(open_action)
        menu.addAction(wear_action)
        menu.addSeparator()
        menu.addAction(properties_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        
        # Connect signals
        open_action.triggered.connect(lambda: self.on_item_open(item))
        wear_action.triggered.connect(lambda: self.on_item_wear(item))
        properties_action.triggered.connect(lambda: self.on_item_properties(item))
        delete_action.triggered.connect(lambda: self.on_item_delete(item))
        
        # Show menu
        menu.exec_(self.inventory_tree.viewport().mapToGlobal(position))
        
    def on_item_open(self, item):
        """Handle opening an inventory item"""
        self.logger.info(f"Opening inventory item: {item.text(0)}")
        
    def on_item_wear(self, item):
        """Handle wearing an inventory item"""
        self.logger.info(f"Wearing inventory item: {item.text(0)}")
        
    def on_item_properties(self, item):
        """Handle showing properties for an inventory item"""
        self.logger.info(f"Showing properties for inventory item: {item.text(0)}")
        
    def on_item_delete(self, item):
        """Handle deleting an inventory item"""
        self.logger.info(f"Deleting inventory item: {item.text(0)}")
        
    def refresh_inventory(self):
        """Refresh the inventory display"""
        self.logger.info("Refreshing inventory")
        # Here we would request inventory data from the server
        # For now, just populate with sample data
        self._populate_sample_data()
        
    def create_new_folder(self):
        """Create a new folder in the inventory"""
        self.logger.info("Creating new folder")
        # Add a new folder item to the tree
        current_item = self.inventory_tree.currentItem()
        parent = current_item if current_item else self.inventory_tree.invisibleRootItem()
        
        new_folder = QTreeWidgetItem(parent)
        new_folder.setText(0, "New Folder")
        new_folder.setText(1, "Folder")
        new_folder.setFlags(new_folder.flags() | Qt.ItemIsEditable)
        
        # Expand parent
        parent.setExpanded(True)
        
        # Set focus and start editing
        self.inventory_tree.setCurrentItem(new_folder)
        self.inventory_tree.editItem(new_folder, 0)
        
    def filter_inventory(self, text):
        """Filter inventory items by name"""
        # Hide items that don't match the search text
        if not text:
            # Show all items
            for i in range(self.inventory_tree.topLevelItemCount()):
                self._set_item_visible(self.inventory_tree.topLevelItem(i), True)
        else:
            # Hide items that don't match
            for i in range(self.inventory_tree.topLevelItemCount()):
                item = self.inventory_tree.topLevelItem(i)
                self._filter_item(item, text.lower())
                
    def _filter_item(self, item, text):
        """Recursively filter item and its children"""
        visible = False
        
        # Check if this item matches
        if text in item.text(0).lower():
            visible = True
        
        # Check children
        for i in range(item.childCount()):
            if self._filter_item(item.child(i), text):
                visible = True
                
        # Set visibility
        self._set_item_visible(item, visible)
        return visible
        
    def _set_item_visible(self, item, visible):
        """Set item visibility in tree"""
        item.setHidden(not visible)
        
    def apply_filter(self, index):
        """Apply a filter to the inventory"""
        filter_type = self.filter_combo.currentText()
        self.logger.info(f"Applying filter: {filter_type}")
        # Here we would apply the selected filter
        # For now, just log the action
        
    def _populate_sample_data(self):
        """Populate the inventory tree with sample data"""
        self.inventory_tree.clear()
        
        # Create root folder
        self.root_folder = QTreeWidgetItem(self.inventory_tree)
        self.root_folder.setText(0, "My Inventory")
        self.root_folder.setText(1, "Root")
        
        # Create some standard folders
        folders = {
            "Clothing": QTreeWidgetItem(self.root_folder),
            "Objects": QTreeWidgetItem(self.root_folder),
            "Textures": QTreeWidgetItem(self.root_folder),
            "Animations": QTreeWidgetItem(self.root_folder),
            "Landmarks": QTreeWidgetItem(self.root_folder)
        }
        
        # Set folder names
        for name, item in folders.items():
            item.setText(0, name)
            item.setText(1, "Folder")
        
        # Add some sample items to folders
        clothing_items = [
            ("Blue Shirt", "Clothing"),
            ("Black Pants", "Clothing"),
            ("Red Dress", "Clothing")
        ]
        
        object_items = [
            ("Chair", "Object"),
            ("Table", "Object"),
            ("Lamp", "Object")
        ]
        
        texture_items = [
            ("Wood Texture", "Texture"),
            ("Fabric Texture", "Texture"),
            ("Metal Texture", "Texture")
        ]
        
        # Add clothing items
        for name, item_type in clothing_items:
            item = QTreeWidgetItem(folders["Clothing"])
            item.setText(0, name)
            item.setText(1, item_type)
            
        # Add object items
        for name, item_type in object_items:
            item = QTreeWidgetItem(folders["Objects"])
            item.setText(0, name)
            item.setText(1, item_type)
            
        # Add texture items
        for name, item_type in texture_items:
            item = QTreeWidgetItem(folders["Textures"])
            item.setText(0, name)
            item.setText(1, item_type)
            
        # Expand root folder
        self.root_folder.setExpanded(True)
        
    def on_login_success(self):
        """Handle successful login"""
        # Populate inventory with sample data
        self._populate_sample_data()
        
    def on_logout(self):
        """Handle logout"""
        # Clear inventory
        self.inventory_tree.clear()
        self.root_folder = None