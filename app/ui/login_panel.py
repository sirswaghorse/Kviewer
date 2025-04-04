"""
Login panel for the KitelyView viewer.
Handles user authentication to the Kitely grid.
"""

import wx
import wx.html
import threading
import logging
import io
from PIL import Image
from app.network.connection import GridConnection

class LoginPanel(wx.Panel):
    """Panel for handling login to the Kitely grid"""
    
    def __init__(self, parent):
        """Initialize the login panel"""
        wx.Panel.__init__(self, parent, size=(400, 300))
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.login_panel")
        self.logger.info("Initializing login panel")
        
        # Store parent reference (MainWindow)
        self.main_window = parent
        
        # Create grid connection
        self.connection = GridConnection(self.main_window.config)
        
        # Set up panel style and layout
        self.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        # Create UI elements
        self._create_ui()
        
        # Bind events
        self.login_button.Bind(wx.EVT_BUTTON, self.on_login)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.grid_choice.Bind(wx.EVT_CHOICE, self.on_grid_change)
        
        # Load grid info
        self._load_grid_info()
        
        self.logger.info("Login panel initialized")
        
    def _create_ui(self):
        """Create UI elements"""
        # Create main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add logo/banner
        logo_text = wx.StaticText(self, label="KitelyView", style=wx.ALIGN_CENTER)
        font = logo_text.GetFont()
        font.SetPointSize(24)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        logo_text.SetFont(font)
        main_sizer.Add(logo_text, 0, wx.ALL | wx.EXPAND, 10)
        
        # Add grid selector
        grid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        grid_label = wx.StaticText(self, label="Grid:")
        self.grid_choice = wx.Choice(self, choices=["Kitely"])
        grid_sizer.Add(grid_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer.Add(self.grid_choice, 1, wx.ALL, 5)
        main_sizer.Add(grid_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # Username field
        username_sizer = wx.BoxSizer(wx.HORIZONTAL)
        username_label = wx.StaticText(self, label="Username:")
        self.username_ctrl = wx.TextCtrl(self)
        username_sizer.Add(username_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        username_sizer.Add(self.username_ctrl, 1, wx.ALL, 5)
        main_sizer.Add(username_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # Password field
        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        password_label = wx.StaticText(self, label="Password:")
        self.password_ctrl = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        password_sizer.Add(password_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        password_sizer.Add(self.password_ctrl, 1, wx.ALL, 5)
        main_sizer.Add(password_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # Location field
        location_sizer = wx.BoxSizer(wx.HORIZONTAL)
        location_label = wx.StaticText(self, label="Location:")
        self.location_ctrl = wx.TextCtrl(self, value="last")
        location_sizer.Add(location_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        location_sizer.Add(self.location_ctrl, 1, wx.ALL, 5)
        main_sizer.Add(location_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # Remember password checkbox
        self.remember_checkbox = wx.CheckBox(self, label="Remember password")
        main_sizer.Add(self.remember_checkbox, 0, wx.ALL, 10)
        
        # Status message
        self.status_text = wx.StaticText(self, label="")
        self.status_text.SetForegroundColour(wx.Colour(200, 0, 0))
        main_sizer.Add(self.status_text, 0, wx.ALL | wx.EXPAND, 5)
        
        # Progress indicator
        self.progress = wx.Gauge(self, range=100, style=wx.GA_HORIZONTAL)
        self.progress.SetValue(0)
        self.progress.Hide()
        main_sizer.Add(self.progress, 0, wx.ALL | wx.EXPAND, 10)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.login_button = wx.Button(self, label="Login")
        self.cancel_button = wx.Button(self, label="Cancel")
        
        self.login_button.SetDefault()
        
        button_sizer.Add(self.login_button, 1, wx.ALL, 5)
        button_sizer.Add(self.cancel_button, 1, wx.ALL, 5)
        
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # Add register and help links
        link_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        register_link = wx.adv.HyperlinkCtrl(
            self,
            wx.ID_ANY,
            "Register Account",
            "https://www.kitely.com/register"
        )
        help_link = wx.adv.HyperlinkCtrl(
            self,
            wx.ID_ANY,
            "Need Help?",
            "https://www.kitely.com/virtual-world-help"
        )
        
        link_sizer.Add(register_link, 0, wx.ALL, 5)
        link_sizer.AddStretchSpacer()
        link_sizer.Add(help_link, 0, wx.ALL, 5)
        
        main_sizer.Add(link_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # Set sizer
        self.SetSizer(main_sizer)
        
    def _load_grid_info(self):
        """Load grid information"""
        # Set default grid to Kitely
        self.grid_choice.SetSelection(0)
        
        # In the future, could load from a configuration file with multiple grids
        
    def on_grid_change(self, event):
        """Handle grid selection change"""
        # Currently only Kitely is supported
        pass
        
    def on_login(self, event):
        """Handle login button press"""
        # Get login credentials
        username = self.username_ctrl.GetValue().strip()
        password = self.password_ctrl.GetValue().strip()
        location = self.location_ctrl.GetValue().strip()
        
        # Validate input
        if not username:
            self.show_error("Please enter a username")
            return
            
        if not password:
            self.show_error("Please enter a password")
            return
            
        # Parse username into first/last name if needed
        user_parts = username.split(' ')
        if len(user_parts) == 1:
            # Assume the format is first.last
            name_parts = username.split('.')
            if len(name_parts) == 2:
                first_name = name_parts[0]
                last_name = name_parts[1]
            else:
                self.show_error("Invalid username format. Use 'First Last' or 'First.Last'")
                return
        else:
            first_name = user_parts[0]
            last_name = ' '.join(user_parts[1:])
            
        # Show progress indicator
        self.progress.Show()
        self.progress.SetValue(10)
        self.login_button.Disable()
        self.cancel_button.Disable()
        self.status_text.SetLabel("Connecting to grid...")
        
        # Use a thread for login to avoid freezing the UI
        threading.Thread(
            target=self._login_thread,
            args=(first_name, last_name, password, location),
            daemon=True
        ).start()
        
    def _login_thread(self, first_name, last_name, password, location):
        """Thread for handling login process"""
        try:
            # Update progress
            wx.CallAfter(self.progress.SetValue, 30)
            wx.CallAfter(self.status_text.SetLabel, "Authenticating...")
            
            # Attempt login
            success, result = self.connection.login(first_name, last_name, password, location)
            
            if success:
                # Update progress
                wx.CallAfter(self.progress.SetValue, 70)
                wx.CallAfter(self.status_text.SetLabel, "Loading world...")
                
                # Handle successful login
                wx.CallAfter(self._login_success, result)
            else:
                # Handle login failure
                wx.CallAfter(self.show_error, f"Login failed: {result}")
                wx.CallAfter(self.progress.Hide)
                wx.CallAfter(self.login_button.Enable)
                wx.CallAfter(self.cancel_button.Enable)
                
        except Exception as e:
            # Handle unexpected errors
            wx.CallAfter(self.show_error, f"Error during login: {str(e)}")
            wx.CallAfter(self.progress.Hide)
            wx.CallAfter(self.login_button.Enable)
            wx.CallAfter(self.cancel_button.Enable)
            self.logger.error(f"Login error: {e}", exc_info=True)
    
    def _login_success(self, user_data):
        """Handle successful login"""
        # Update progress
        self.progress.SetValue(100)
        
        # Save username (not password) for next time
        # TODO: Implement config saving
        
        # Notify the main window
        self.main_window.login_success(user_data)
        
        # Reset UI
        self.progress.Hide()
        self.login_button.Enable()
        self.cancel_button.Enable()
        self.status_text.SetLabel("")
        
        # If not remembering password, clear it
        if not self.remember_checkbox.GetValue():
            self.password_ctrl.SetValue("")
    
    def on_cancel(self, event):
        """Handle cancel button press"""
        # Hide the login panel
        self.main_window.aui_manager.GetPane(self).Hide()
        self.main_window.aui_manager.Update()
        
        # Clear any error message
        self.status_text.SetLabel("")
        
        # If login is in progress, cancel it
        if not self.login_button.IsEnabled():
            # TODO: Implement cancel logic for the connection
            self.login_button.Enable()
            self.cancel_button.Enable()
            self.progress.Hide()
    
    def show_error(self, message):
        """Display an error message"""
        self.status_text.SetLabel(message)
