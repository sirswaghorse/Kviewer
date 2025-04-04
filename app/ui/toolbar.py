"""
Toolbar implementation for the KitelyView viewer.
Provides access to common actions and tools.
"""

import wx
import logging

class ViewerToolbar(wx.ToolBar):
    """Toolbar providing access to common viewer actions"""
    
    def __init__(self, parent):
        """Initialize the toolbar"""
        wx.ToolBar.__init__(self, parent, style=wx.TB_HORIZONTAL | wx.TB_TEXT)
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.toolbar")
        self.logger.info("Initializing viewer toolbar")
        
        # Store parent reference
        self.main_window = parent
        
        # Set up toolbar
        self.SetToolBitmapSize((24, 24))
        self.SetToolSeparation(5)
        self._create_tools()
        self.Realize()
        
        self.logger.info("Toolbar initialized")
        
    def _create_tools(self):
        """Create toolbar buttons and tools"""
        # Create tools using standard art provider icons
        
        # Chat tool
        chat_tool = self.AddTool(
            wx.ID_ANY,
            "Chat",
            wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_TOOLBAR, (24, 24)),
            shortHelp="Open Chat"
        )
        
        # Inventory tool
        inventory_tool = self.AddTool(
            wx.ID_ANY,
            "Inventory",
            wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, wx.ART_TOOLBAR, (24, 24)),
            shortHelp="Open Inventory"
        )
        
        # Map tool
        map_tool = self.AddTool(
            wx.ID_ANY,
            "Map",
            wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_TOOLBAR, (24, 24)),
            shortHelp="Open Map"
        )
        
        self.AddSeparator()
        
        # Movement controls
        fly_tool = self.AddTool(
            wx.ID_ANY,
            "Fly",
            wx.ArtProvider.GetBitmap(wx.ART_GO_UP, wx.ART_TOOLBAR, (24, 24)),
            shortHelp="Toggle Fly Mode",
            kind=wx.ITEM_CHECK
        )
        
        self.AddSeparator()
        
        # Building tools
        build_tool = self.AddTool(
            wx.ID_ANY,
            "Build",
            wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, (24, 24)),
            shortHelp="Build Mode",
            kind=wx.ITEM_CHECK
        )
        
        # Add another separator
        self.AddSeparator()
        
        # Search tool
        search_tool = self.AddTool(
            wx.ID_ANY,
            "Search",
            wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_TOOLBAR, (24, 24)),
            shortHelp="Search"
        )
        
        # Settings tool
        settings_tool = self.AddTool(
            wx.ID_ANY,
            "Settings",
            wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_TOOLBAR, (24, 24)),
            shortHelp="Settings"
        )
        
        # Bind events
        self.Bind(wx.EVT_TOOL, self.on_chat, chat_tool)
        self.Bind(wx.EVT_TOOL, self.on_inventory, inventory_tool)
        self.Bind(wx.EVT_TOOL, self.on_map, map_tool)
        self.Bind(wx.EVT_TOOL, self.on_fly, fly_tool)
        self.Bind(wx.EVT_TOOL, self.on_build, build_tool)
        self.Bind(wx.EVT_TOOL, self.on_search, search_tool)
        self.Bind(wx.EVT_TOOL, self.on_settings, settings_tool)
        
    def on_chat(self, event):
        """Show/hide chat panel"""
        pane = self.main_window.aui_manager.GetPane("chat")
        if pane.IsShown():
            pane.Hide()
        else:
            pane.Show()
        self.main_window.aui_manager.Update()
        
    def on_inventory(self, event):
        """Show/hide inventory panel"""
        pane = self.main_window.aui_manager.GetPane("inventory")
        if pane.IsShown():
            pane.Hide()
        else:
            pane.Show()
        self.main_window.aui_manager.Update()
        
    def on_map(self, event):
        """Show/hide mini map panel"""
        pane = self.main_window.aui_manager.GetPane("mini_map")
        if pane.IsShown():
            pane.Hide()
        else:
            pane.Show()
        self.main_window.aui_manager.Update()
        
    def on_fly(self, event):
        """Toggle fly mode"""
        # Only works when logged in
        if not self.main_window.is_logged_in:
            self.ToggleTool(event.GetId(), False)
            wx.MessageBox("You must be logged in to use this feature", "Not Logged In", wx.OK | wx.ICON_INFORMATION)
            return
            
        # Toggle fly mode in the scene view
        is_flying = event.GetInt() == 1
        if hasattr(self.main_window, 'world_view'):
            # Notify the world view to update the movement mode
            # This would implement actual flying mode in a full viewer
            self.logger.info(f"Fly mode {'enabled' if is_flying else 'disabled'}")
            self.main_window.update_status(f"Fly mode {'enabled' if is_flying else 'disabled'}")
        
    def on_build(self, event):
        """Toggle build mode"""
        # Only works when logged in
        if not self.main_window.is_logged_in:
            self.ToggleTool(event.GetId(), False)
            wx.MessageBox("You must be logged in to use this feature", "Not Logged In", wx.OK | wx.ICON_INFORMATION)
            return
            
        # Toggle build mode 
        is_building = event.GetInt() == 1
        self.logger.info(f"Build mode {'enabled' if is_building else 'disabled'}")
        self.main_window.update_status(f"Build mode {'enabled' if is_building else 'disabled'}")
        
    def on_search(self, event):
        """Open search dialog"""
        # Only works when logged in
        if not self.main_window.is_logged_in:
            wx.MessageBox("You must be logged in to use this feature", "Not Logged In", wx.OK | wx.ICON_INFORMATION)
            return
            
        # Would open a search dialog in a full implementation
        wx.MessageBox("Search functionality not yet implemented", "Coming Soon", wx.OK | wx.ICON_INFORMATION)
        
    def on_settings(self, event):
        """Open settings dialog"""
        # Would open a settings dialog in a full implementation
        wx.MessageBox("Settings dialog not yet implemented", "Coming Soon", wx.OK | wx.ICON_INFORMATION)
