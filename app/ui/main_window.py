"""
Main window for the KitelyView application.
Integrates all UI components and manages the application layout.
"""

import wx
import wx.lib.agw.aui as aui
import logging
import os
from app.ui.login_panel import LoginPanel
from app.ui.world_view import WorldViewPanel
from app.ui.chat_panel import ChatPanel
from app.ui.inventory_panel import InventoryPanel
from app.ui.mini_map import MiniMapPanel
from app.ui.toolbar import ViewerToolbar
from app.renderer.scene import Scene
from app.network.connection import GridConnection
from app.models.user import User

class MainWindow(wx.Frame):
    """Main application window"""
    
    def __init__(self, config):
        """Initialize the main window"""
        # Get window size from config
        resolution = config.get("viewer", "resolution")
        
        # Call parent constructor
        wx.Frame.__init__(
            self,
            None,
            title="KitelyView - OpenSimulator Viewer",
            size=resolution,
            style=wx.DEFAULT_FRAME_STYLE
        )
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.main_window")
        self.logger.info("Initializing main window")
        
        # Store configuration
        self.config = config
        
        # Set application icon
        self._set_application_icon()
        
        # Initialize class variables
        self.is_logged_in = False
        self.user = User()
        self.connection = GridConnection(config)
        self.scene = Scene(self)
        
        # Create AUI manager
        self.aui_manager = aui.AuiManager(self)
        
        # Create UI components
        self._create_menu_bar()
        self._create_status_bar()
        self._create_panels()
        
        # Bind event handlers
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        # Center on screen
        self.Centre()
        
        # Set up fullscreen if configured
        if config.get("viewer", "fullscreen"):
            self.ShowFullScreen(True)
            
        self.logger.info("Main window initialized")
        
    def _set_application_icon(self):
        """Set the application icon"""
        try:
            # Use wx bundled icon to avoid binary file issues
            icon = wx.ArtProvider.GetIcon(wx.ART_INFORMATION, wx.ART_FRAME_ICON)
            self.SetIcon(icon)
        except Exception as e:
            self.logger.error(f"Failed to set application icon: {e}")
    
    def _create_menu_bar(self):
        """Create the application menu bar"""
        menubar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        login_item = file_menu.Append(wx.ID_ANY, "&Login\tCtrl+L", "Login to Kitely grid")
        logout_item = file_menu.Append(wx.ID_ANY, "Log&out\tCtrl+O", "Logout from grid")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4", "Exit the application")
        
        # Edit menu
        edit_menu = wx.Menu()
        preferences_item = edit_menu.Append(wx.ID_PREFERENCES, "&Preferences\tCtrl+P", "Edit preferences")
        
        # View menu
        view_menu = wx.Menu()
        fullscreen_item = view_menu.Append(wx.ID_ANY, "&Fullscreen\tF11", "Toggle fullscreen mode", kind=wx.ITEM_CHECK)
        view_menu.AppendSeparator()
        reset_layout_item = view_menu.Append(wx.ID_ANY, "&Reset Layout", "Reset the window layout")
        
        # Help menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About\tF1", "About KitelyView")
        
        # Add menus to menubar
        menubar.Append(file_menu, "&File")
        menubar.Append(edit_menu, "&Edit")
        menubar.Append(view_menu, "&View")
        menubar.Append(help_menu, "&Help")
        
        # Set menubar
        self.SetMenuBar(menubar)
        
        # Bind events
        self.Bind(wx.EVT_MENU, self.on_login, login_item)
        self.Bind(wx.EVT_MENU, self.on_logout, logout_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_preferences, preferences_item)
        self.Bind(wx.EVT_MENU, self.on_toggle_fullscreen, fullscreen_item)
        self.Bind(wx.EVT_MENU, self.on_reset_layout, reset_layout_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
        
    def _create_status_bar(self):
        """Create the status bar"""
        self.status_bar = self.CreateStatusBar(3)
        self.status_bar.SetStatusWidths([-3, -1, -2])
        self.update_status("Ready")
        
    def _create_panels(self):
        """Create and arrange UI panels"""
        # Create the toolbar
        self.toolbar = ViewerToolbar(self)
        self.SetToolBar(self.toolbar)
        
        # Create panels
        self.world_view = WorldViewPanel(self)
        self.login_panel = LoginPanel(self)
        self.chat_panel = ChatPanel(self)
        self.inventory_panel = InventoryPanel(self)
        self.mini_map = MiniMapPanel(self)
        
        # Add panels to AUI manager
        self.aui_manager.AddPane(
            self.world_view,
            aui.AuiPaneInfo().Name("world_view").CenterPane().Caption("World View")
        )
        
        self.aui_manager.AddPane(
            self.login_panel,
            aui.AuiPaneInfo().Name("login").Float().Caption("Login").
            CloseButton(False).MaximizeButton(False).MinimizeButton(False).
            Dockable(False).Show(not self.is_logged_in)
        )
        
        self.aui_manager.AddPane(
            self.chat_panel,
            aui.AuiPaneInfo().Name("chat").Bottom().Caption("Chat").
            BestSize(wx.Size(-1, 200)).MinSize(wx.Size(-1, 100)).
            Show(self.is_logged_in)
        )
        
        self.aui_manager.AddPane(
            self.inventory_panel,
            aui.AuiPaneInfo().Name("inventory").Right().Caption("Inventory").
            BestSize(wx.Size(250, -1)).MinSize(wx.Size(200, -1)).
            Show(self.is_logged_in)
        )
        
        self.aui_manager.AddPane(
            self.mini_map,
            aui.AuiPaneInfo().Name("mini_map").Right().Caption("Mini Map").
            BestSize(wx.Size(250, 250)).MinSize(wx.Size(200, 200)).
            Show(self.is_logged_in)
        )
        
        # Update the AUI manager
        self.aui_manager.Update()
        
    def update_status(self, text, position=0):
        """Update the status bar text"""
        if self.status_bar:
            self.status_bar.SetStatusText(text, position)
            
    def on_login(self, event):
        """Handle login menu click"""
        if not self.is_logged_in:
            login_pane = self.aui_manager.GetPane("login")
            if not login_pane.IsShown():
                login_pane.Show()
                self.aui_manager.Update()
    
    def login_success(self, user_data):
        """Handle successful login"""
        self.is_logged_in = True
        self.user = User(user_data)
        
        # Update UI
        self.aui_manager.GetPane("login").Hide()
        self.aui_manager.GetPane("chat").Show()
        self.aui_manager.GetPane("inventory").Show()
        self.aui_manager.GetPane("mini_map").Show()
        self.aui_manager.Update()
        
        # Update status
        self.update_status(f"Logged in as {self.user.first_name} {self.user.last_name}")
        
        # Notify components
        self.world_view.on_login_success()
        self.chat_panel.on_login_success()
        self.inventory_panel.on_login_success()
        self.mini_map.on_login_success()
        
        self.logger.info(f"User logged in: {self.user.first_name} {self.user.last_name}")
    
    def on_logout(self, event):
        """Handle logout request"""
        if self.is_logged_in:
            dlg = wx.MessageDialog(
                self,
                "Are you sure you want to log out?",
                "Confirm Logout",
                wx.YES_NO | wx.ICON_QUESTION
            )
            result = dlg.ShowModal()
            dlg.Destroy()
            
            if result == wx.ID_YES:
                self.logout()
    
    def logout(self):
        """Perform logout"""
        if self.is_logged_in:
            # Disconnect from grid
            self.connection.disconnect()
            
            # Reset user
            self.is_logged_in = False
            self.user = User()
            
            # Update UI
            self.aui_manager.GetPane("login").Show()
            self.aui_manager.GetPane("chat").Hide()
            self.aui_manager.GetPane("inventory").Hide()
            self.aui_manager.GetPane("mini_map").Hide()
            self.aui_manager.Update()
            
            # Update status
            self.update_status("Logged out")
            
            # Notify components
            self.world_view.on_logout()
            self.chat_panel.on_logout()
            self.inventory_panel.on_logout()
            self.mini_map.on_logout()
            
            self.logger.info("User logged out")
    
    def on_exit(self, event):
        """Handle exit request"""
        self.Close()
    
    def on_preferences(self, event):
        """Show preferences dialog"""
        # To be implemented
        wx.MessageBox("Preferences dialog not yet implemented", "Information", wx.OK | wx.ICON_INFORMATION)
    
    def on_toggle_fullscreen(self, event):
        """Toggle fullscreen mode"""
        self.ShowFullScreen(not self.IsFullScreen())
    
    def on_reset_layout(self, event):
        """Reset the window layout to default"""
        # Save current state to detect what's visible
        is_logged_in = self.is_logged_in
        
        # Close all panes
        self.aui_manager.DetachPane(self.world_view)
        self.aui_manager.DetachPane(self.login_panel)
        self.aui_manager.DetachPane(self.chat_panel)
        self.aui_manager.DetachPane(self.inventory_panel)
        self.aui_manager.DetachPane(self.mini_map)
        
        # Recreate panes with default layout
        self.aui_manager.AddPane(
            self.world_view,
            aui.AuiPaneInfo().Name("world_view").CenterPane().Caption("World View")
        )
        
        self.aui_manager.AddPane(
            self.login_panel,
            aui.AuiPaneInfo().Name("login").Float().Caption("Login").
            CloseButton(False).MaximizeButton(False).MinimizeButton(False).
            Dockable(False).Show(not is_logged_in)
        )
        
        self.aui_manager.AddPane(
            self.chat_panel,
            aui.AuiPaneInfo().Name("chat").Bottom().Caption("Chat").
            BestSize(wx.Size(-1, 200)).MinSize(wx.Size(-1, 100)).
            Show(is_logged_in)
        )
        
        self.aui_manager.AddPane(
            self.inventory_panel,
            aui.AuiPaneInfo().Name("inventory").Right().Caption("Inventory").
            BestSize(wx.Size(250, -1)).MinSize(wx.Size(200, -1)).
            Show(is_logged_in)
        )
        
        self.aui_manager.AddPane(
            self.mini_map,
            aui.AuiPaneInfo().Name("mini_map").Right().Caption("Mini Map").
            BestSize(wx.Size(250, 250)).MinSize(wx.Size(200, 200)).
            Show(is_logged_in)
        )
        
        # Update the AUI manager
        self.aui_manager.Update()
        
        self.logger.info("Layout reset to default")
    
    def on_about(self, event):
        """Show about dialog"""
        info = wx.adv.AboutDialogInfo()
        info.SetName("KitelyView")
        info.SetVersion("0.1.0")
        info.SetDescription("A cross-platform OpenSimulator viewer for connecting to the Kitely grid.")
        info.SetCopyright("(C) 2023")
        info.SetWebSite("https://www.kitely.com")
        info.AddDeveloper("KitelyView Development Team")
        info.SetLicense("MIT License")
        
        wx.adv.AboutBox(info)
    
    def on_close(self, event):
        """Handle window close event"""
        if self.is_logged_in:
            dlg = wx.MessageDialog(
                self,
                "You are still logged in. Log out and close the application?",
                "Confirm Exit",
                wx.YES_NO | wx.ICON_QUESTION
            )
            result = dlg.ShowModal()
            dlg.Destroy()
            
            if result == wx.ID_YES:
                self.connection.disconnect()
                self.destroy_app()
            else:
                event.Skip(False)  # Prevent closing
        else:
            self.destroy_app()
    
    def destroy_app(self):
        """Clean up and destroy the application"""
        self.logger.info("Shutting down application")
        
        # Uninit AUI manager
        self.aui_manager.UnInit()
        
        # Save configuration
        self.config.save_config()
        
        # Destroy the window
        self.Destroy()
