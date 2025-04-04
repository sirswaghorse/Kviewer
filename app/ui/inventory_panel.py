"""
Inventory panel for the KitelyView application.
Displays and manages the user's inventory items.
"""

import wx
import logging
import time

class InventoryPanel(wx.Panel):
    """Panel for managing user inventory"""
    
    def __init__(self, parent):
        """Initialize the inventory panel"""
        wx.Panel.__init__(self, parent)
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.inventory_panel")
        self.logger.info("Initializing inventory panel")
        
        # Store parent reference
        self.main_window = parent
        
        # Inventory data
        self.inventory_root = None
        self.inventory_items = {}
        
        # UI setup
        self._create_ui()
        
        # Bind events
        self.filter_text.Bind(wx.EVT_TEXT, self.on_filter_changed)
        self.inventory_tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_item_activated)
        self.inventory_tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_item_right_click)
        
        self.logger.info("Inventory panel initialized")
        
    def _create_ui(self):
        """Create UI elements"""
        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create toolbar for inventory actions
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Filter text
        self.filter_text = wx.SearchCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.filter_text.SetDescriptiveText("Filter items...")
        toolbar_sizer.Add(self.filter_text, 1, wx.EXPAND | wx.ALL, 2)
        
        # Refresh button
        self.refresh_button = wx.Button(self, label="⟳", size=(28, 28))
        self.refresh_button.SetToolTip("Refresh inventory")
        self.refresh_button.Bind(wx.EVT_BUTTON, self.on_refresh)
        toolbar_sizer.Add(self.refresh_button, 0, wx.ALL, 2)
        
        main_sizer.Add(toolbar_sizer, 0, wx.EXPAND)
        
        # Create inventory tree control
        self.inventory_tree = wx.TreeCtrl(
            self,
            style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_MULTIPLE | wx.TR_EDIT_LABELS
        )
        
        # Create image list for tree icons
        self.image_list = wx.ImageList(16, 16)
        # Create icons from built-in art provider
        self.folder_icon = self.image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16))
        )
        self.file_icon = self.image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16))
        )
        self.clothing_icon = self.image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_HELP_SIDE_PANEL, wx.ART_OTHER, (16, 16))
        )
        self.object_icon = self.image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_REPORT_VIEW, wx.ART_OTHER, (16, 16))
        )
        self.texture_icon = self.image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE, wx.ART_OTHER, (16, 16))
        )
        self.script_icon = self.image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_OTHER, (16, 16))
        )
        
        # Set image list
        self.inventory_tree.SetImageList(self.image_list)
        
        # Add invisible root
        self.inventory_tree.AddRoot("Inventory")
        
        main_sizer.Add(self.inventory_tree, 1, wx.EXPAND | wx.ALL, 5)
        
        # Create progress indicator for loading
        self.progress = wx.Gauge(self, range=100)
        self.progress.Hide()
        main_sizer.Add(self.progress, 0, wx.EXPAND | wx.ALL, 5)
        
        # Set sizer
        self.SetSizer(main_sizer)
        
    def on_filter_changed(self, event):
        """Handle filter text changes"""
        # Get filter text
        filter_text = self.filter_text.GetValue().lower()
        
        # If empty, just reload the full inventory
        if not filter_text:
            self.populate_inventory()
            return
            
        # Otherwise, apply the filter
        self.apply_filter(filter_text)
        
    def apply_filter(self, filter_text):
        """Filter inventory items by name"""
        # Clear tree
        self.inventory_tree.DeleteAllItems()
        root = self.inventory_tree.AddRoot("Inventory")
        
        # If no inventory loaded yet, return
        if not self.inventory_root:
            return
            
        # Create filtered categories
        filtered_items = {}
        
        # Add matching items to filtered tree
        for item_id, item in self.inventory_items.items():
            if filter_text in item["name"].lower():
                # Get or create parent folder
                parent_id = item.get("parent_id")
                
                if parent_id not in filtered_items:
                    # Create parent folder if needed
                    if parent_id in self.inventory_items:
                        parent_item = self.inventory_items[parent_id]
                        parent_node = self.inventory_tree.AppendItem(
                            root,
                            parent_item["name"],
                            self.folder_icon
                        )
                        filtered_items[parent_id] = parent_node
                    else:
                        # If parent not found, add under root
                        parent_node = root
                else:
                    parent_node = filtered_items[parent_id]
                
                # Add item to tree
                icon = self.get_icon_for_type(item["type"])
                tree_item = self.inventory_tree.AppendItem(
                    parent_node,
                    item["name"],
                    icon
                )
                self.inventory_tree.SetItemData(tree_item, item_id)
        
        # Expand all items for easier viewing of filtered results
        self.inventory_tree.ExpandAll()
        
    def get_icon_for_type(self, item_type):
        """Get the appropriate icon for the item type"""
        if item_type == "folder":
            return self.folder_icon
        elif item_type == "clothing":
            return self.clothing_icon
        elif item_type == "object":
            return self.object_icon
        elif item_type == "texture":
            return self.texture_icon
        elif item_type == "script":
            return self.script_icon
        else:
            return self.file_icon
        
    def populate_inventory(self):
        """Populate the inventory tree with user's items"""
        # Clear tree
        self.inventory_tree.DeleteAllItems()
        root = self.inventory_tree.AddRoot("Inventory")
        
        # If no inventory loaded yet, return
        if not self.inventory_root:
            self.inventory_tree.AppendItem(root, "Loading inventory...")
            return
            
        # Track tree items by ID for quick access
        tree_items = {}
        tree_items[self.inventory_root] = root
        
        # First pass: create all folders
        for item_id, item in self.inventory_items.items():
            if item["type"] == "folder":
                parent_id = item.get("parent_id", self.inventory_root)
                
                # Skip if parent not found (shouldn't happen in well-formed inventory)
                if parent_id not in tree_items:
                    if parent_id != self.inventory_root:
                        continue
                        
                # Create folder
                tree_item = self.inventory_tree.AppendItem(
                    tree_items[parent_id],
                    item["name"],
                    self.folder_icon
                )
                self.inventory_tree.SetItemData(tree_item, item_id)
                tree_items[item_id] = tree_item
                
        # Second pass: add all items
        for item_id, item in self.inventory_items.items():
            if item["type"] != "folder":
                parent_id = item.get("parent_id", self.inventory_root)
                
                # Skip if parent not found
                if parent_id not in tree_items:
                    continue
                    
                # Create item
                icon = self.get_icon_for_type(item["type"])
                tree_item = self.inventory_tree.AppendItem(
                    tree_items[parent_id],
                    item["name"],
                    icon
                )
                self.inventory_tree.SetItemData(tree_item, item_id)
                
        # Expand root category folders
        child, cookie = self.inventory_tree.GetFirstChild(root)
        while child.IsOk():
            self.inventory_tree.Expand(child)
            child, cookie = self.inventory_tree.GetNextChild(root, cookie)
        
    def load_inventory(self):
        """Load inventory from the grid"""
        # Show progress indicator
        self.progress.Show()
        self.progress.SetValue(0)
        
        # Clear existing inventory
        self.inventory_items = {}
        
        # In a real application, this would fetch from the server
        # For now, create a sample inventory structure
        self.create_sample_inventory()
        
        # Populate the inventory tree
        self.populate_inventory()
        
        # Hide progress
        self.progress.Hide()
        
    def create_sample_inventory(self):
        """Create a sample inventory for testing"""
        # This would normally come from the server
        
        # Create root
        self.inventory_root = "inventory_root"
        
        # Create basic structure
        self.inventory_items = {
            "inventory_root": {
                "name": "My Inventory",
                "type": "folder",
                "parent_id": None
            },
            "folder_1": {
                "name": "Clothing",
                "type": "folder",
                "parent_id": "inventory_root"
            },
            "folder_2": {
                "name": "Objects",
                "type": "folder",
                "parent_id": "inventory_root"
            },
            "folder_3": {
                "name": "Textures",
                "type": "folder",
                "parent_id": "inventory_root"
            },
            "folder_4": {
                "name": "Scripts",
                "type": "folder",
                "parent_id": "inventory_root"
            },
            "folder_5": {
                "name": "Notecards",
                "type": "folder",
                "parent_id": "inventory_root"
            },
            "folder_6": {
                "name": "Body Parts",
                "type": "folder",
                "parent_id": "inventory_root"
            },
            "folder_7": {
                "name": "Animations",
                "type": "folder",
                "parent_id": "inventory_root"
            },
            "folder_8": {
                "name": "Landmarks",
                "type": "folder",
                "parent_id": "inventory_root"
            },
            "folder_9": {
                "name": "Shirts",
                "type": "folder",
                "parent_id": "folder_1"
            },
            "folder_10": {
                "name": "Pants",
                "type": "folder",
                "parent_id": "folder_1"
            },
            "item_1": {
                "name": "Blue Shirt",
                "type": "clothing",
                "parent_id": "folder_9"
            },
            "item_2": {
                "name": "Red Shirt",
                "type": "clothing",
                "parent_id": "folder_9"
            },
            "item_3": {
                "name": "Black Pants",
                "type": "clothing",
                "parent_id": "folder_10"
            },
            "item_4": {
                "name": "Wooden Chair",
                "type": "object",
                "parent_id": "folder_2"
            },
            "item_5": {
                "name": "Table",
                "type": "object",
                "parent_id": "folder_2"
            },
            "item_6": {
                "name": "Brick Texture",
                "type": "texture",
                "parent_id": "folder_3"
            },
            "item_7": {
                "name": "Door Script",
                "type": "script",
                "parent_id": "folder_4"
            }
        }
        
        # Simulate loading time
        time.sleep(0.5)
        
    def on_item_activated(self, event):
        """Handle item double-click"""
        # Get selected item
        item_id = self.inventory_tree.GetItemData(event.GetItem())
        
        # If no data, return
        if not item_id:
            return
            
        # Get item details
        item = self.inventory_items.get(item_id)
        if not item:
            return
            
        # Handle different item types
        if item["type"] == "folder":
            # Toggle expansion
            if self.inventory_tree.IsExpanded(event.GetItem()):
                self.inventory_tree.Collapse(event.GetItem())
            else:
                self.inventory_tree.Expand(event.GetItem())
        else:
            # For non-folders, show item properties
            self.show_item_properties(item)
            
    def on_item_right_click(self, event):
        """Handle item right-click"""
        # Get selected item
        item_id = self.inventory_tree.GetItemData(event.GetItem())
        
        # If no data, return
        if not item_id:
            return
            
        # Get item details
        item = self.inventory_items.get(item_id)
        if not item:
            return
            
        # Create context menu
        menu = wx.Menu()
        
        # Add common options
        menu.Append(wx.ID_PROPERTIES, "Properties")
        menu.Append(wx.ID_RENAME, "Rename")
        menu.Append(wx.ID_DELETE, "Delete")
        
        # Add type-specific options
        if item["type"] == "folder":
            menu.AppendSeparator()
            menu.Append(wx.ID_NEW, "New Folder")
        elif item["type"] == "object":
            menu.AppendSeparator()
            menu.Append(wx.ID_ANY, "Rez")
            menu.Append(wx.ID_ANY, "Wear")
        elif item["type"] == "clothing":
            menu.AppendSeparator()
            menu.Append(wx.ID_ANY, "Wear")
            menu.Append(wx.ID_ANY, "Take Off")
        
        # Bind events
        self.Bind(wx.EVT_MENU, lambda e: self.show_item_properties(item), id=wx.ID_PROPERTIES)
        self.Bind(wx.EVT_MENU, lambda e: self.rename_item(event.GetItem()), id=wx.ID_RENAME)
        self.Bind(wx.EVT_MENU, lambda e: self.delete_item(item_id), id=wx.ID_DELETE)
        
        # Show menu
        self.PopupMenu(menu)
        menu.Destroy()
        
    def show_item_properties(self, item):
        """Show item properties dialog"""
        # Create dialog
        dlg = wx.Dialog(self, title=f"Properties: {item['name']}", size=(350, 200))
        
        # Create sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add item details
        grid = wx.FlexGridSizer(cols=2, vgap=5, hgap=10)
        grid.AddGrowableCol(1)
        
        grid.Add(wx.StaticText(dlg, label="Name:"))
        grid.Add(wx.StaticText(dlg, label=item["name"]), flag=wx.EXPAND)
        
        grid.Add(wx.StaticText(dlg, label="Type:"))
        grid.Add(wx.StaticText(dlg, label=item["type"].capitalize()), flag=wx.EXPAND)
        
        if "creator" in item:
            grid.Add(wx.StaticText(dlg, label="Creator:"))
            grid.Add(wx.StaticText(dlg, label=item["creator"]), flag=wx.EXPAND)
            
        if "created" in item:
            grid.Add(wx.StaticText(dlg, label="Created:"))
            grid.Add(wx.StaticText(dlg, label=item["created"]), flag=wx.EXPAND)
            
        sizer.Add(grid, 0, wx.ALL | wx.EXPAND, 10)
        
        # Add OK button
        sizer.Add(dlg.CreateStdDialogButtonSizer(wx.OK), 0, wx.ALL | wx.CENTER, 10)
        
        # Set sizer
        dlg.SetSizer(sizer)
        
        # Show dialog
        dlg.ShowModal()
        dlg.Destroy()
        
    def rename_item(self, tree_item):
        """Rename the selected item"""
        # Begin editing label
        self.inventory_tree.EditLabel(tree_item)
        
    def delete_item(self, item_id):
        """Delete the selected item"""
        # Confirm deletion
        dlg = wx.MessageDialog(
            self,
            f"Are you sure you want to delete '{self.inventory_items[item_id]['name']}'?",
            "Confirm Delete",
            wx.YES_NO | wx.ICON_QUESTION
        )
        result = dlg.ShowModal()
        dlg.Destroy()
        
        if result == wx.ID_YES:
            # In a real app, this would delete on the server
            # For now, just remove from local inventory
            del self.inventory_items[item_id]
            self.populate_inventory()
            
    def on_refresh(self, event):
        """Handle refresh button click"""
        # Reload inventory
        self.load_inventory()
    
    def on_login_success(self):
        """Handle successful login"""
        # Load inventory
        self.load_inventory()
        
    def on_logout(self):
        """Handle logout"""
        # Clear inventory
        self.inventory_items = {}
        self.inventory_root = None
        self.inventory_tree.DeleteAllItems()
        root = self.inventory_tree.AddRoot("Inventory")
        self.inventory_tree.AppendItem(root, "Not logged in")
