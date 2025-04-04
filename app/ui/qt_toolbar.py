"""
Toolbar for the KitelyView viewer using PyQt5.
Provides quick access to common actions.
"""

import logging
from PyQt5.QtWidgets import QToolBar, QAction, QComboBox, QLabel
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

class ViewerToolbar(QToolBar):
    """Toolbar for the viewer application"""
    
    def __init__(self, parent):
        """Initialize the toolbar"""
        super(ViewerToolbar, self).__init__("KitelyView Toolbar", parent)
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.toolbar")
        self.logger.info("Initializing toolbar")
        
        # Store parent reference (MainWindow)
        self.main_window = parent
        
        # Set toolbar properties
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setMovable(False)
        
        # Create toolbar actions
        self._create_actions()
        
        self.logger.info("Toolbar initialized")
        
    def _create_actions(self):
        """Create toolbar actions"""
        # Movement mode selector
        self.addWidget(QLabel("Movement: "))
        self.movement_combo = QComboBox()
        self.movement_combo.addItems(["Walk", "Run", "Fly"])
        self.addWidget(self.movement_combo)
        self.addSeparator()
        
        # Common actions
        self.chat_action = QAction("Chat", self)
        self.chat_action.setStatusTip("Toggle chat panel")
        self.chat_action.triggered.connect(self.toggle_chat)
        self.addAction(self.chat_action)
        
        self.inventory_action = QAction("Inventory", self)
        self.inventory_action.setStatusTip("Toggle inventory panel")
        self.inventory_action.triggered.connect(self.toggle_inventory)
        self.addAction(self.inventory_action)
        
        self.map_action = QAction("Map", self)
        self.map_action.setStatusTip("Toggle mini map")
        self.map_action.triggered.connect(self.toggle_map)
        self.addAction(self.map_action)
        
        self.addSeparator()
        
        # Camera controls
        self.reset_view_action = QAction("Reset View", self)
        self.reset_view_action.setStatusTip("Reset camera view")
        self.reset_view_action.triggered.connect(self.reset_camera)
        self.addAction(self.reset_view_action)
        
        self.addSeparator()
        
        # Build mode
        self.build_action = QAction("Build", self)
        self.build_action.setStatusTip("Enter build mode")
        self.build_action.setCheckable(True)
        self.build_action.triggered.connect(self.toggle_build_mode)
        self.addAction(self.build_action)
        
    def toggle_chat(self):
        """Toggle chat panel visibility"""
        if hasattr(self.main_window, 'chat_dock'):
            visible = self.main_window.chat_dock.isVisible()
            self.main_window.chat_dock.setVisible(not visible)
            self.logger.info(f"Chat panel {'hidden' if visible else 'shown'}")
            
    def toggle_inventory(self):
        """Toggle inventory panel visibility"""
        if hasattr(self.main_window, 'inventory_dock'):
            visible = self.main_window.inventory_dock.isVisible()
            self.main_window.inventory_dock.setVisible(not visible)
            self.logger.info(f"Inventory panel {'hidden' if visible else 'shown'}")
            
    def toggle_map(self):
        """Toggle mini map visibility"""
        if hasattr(self.main_window, 'mini_map_dock'):
            visible = self.main_window.mini_map_dock.isVisible()
            self.main_window.mini_map_dock.setVisible(not visible)
            self.logger.info(f"Mini map {'hidden' if visible else 'shown'}")
            
    def reset_camera(self):
        """Reset camera to default position"""
        if hasattr(self.main_window, 'world_view'):
            self.main_window.world_view.camera.reset()
            self.logger.info("Camera view reset")
            
    def toggle_build_mode(self, checked):
        """Toggle build mode"""
        self.logger.info(f"Build mode {'enabled' if checked else 'disabled'}")
        # Here we would implement changing to build mode
        # For now, just log the action