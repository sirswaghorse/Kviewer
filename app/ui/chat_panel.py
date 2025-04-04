"""
Chat panel for the KitelyView application.
Handles text chat, IM, and channel messaging.
"""

import wx
import wx.richtext
import logging
import time

class ChatPanel(wx.Panel):
    """Panel for chat and messaging functionality"""
    
    def __init__(self, parent):
        """Initialize the chat panel"""
        wx.Panel.__init__(self, parent)
        
        # Set up logging
        self.logger = logging.getLogger("kitelyview.ui.chat_panel")
        self.logger.info("Initializing chat panel")
        
        # Store parent reference
        self.main_window = parent
        
        # Keep track of chat sessions and history
        self.chat_history = {
            "local": []  # Local chat
        }
        self.active_chat = "local"
        
        # UI setup
        self._create_ui()
        
        # Bind events
        self.chat_tabs.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_change)
        self.input_text.Bind(wx.EVT_TEXT_ENTER, self.on_send_message)
        self.send_button.Bind(wx.EVT_BUTTON, self.on_send_message)
        
        self.logger.info("Chat panel initialized")
        
    def _create_ui(self):
        """Create UI elements"""
        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create chat tabs
        self.chat_tabs = wx.Notebook(self)
        
        # Add local chat tab
        self.local_chat = wx.richtext.RichTextCtrl(
            self.chat_tabs,
            style=wx.richtext.RE_MULTILINE | wx.richtext.RE_READONLY
        )
        self.chat_tabs.AddPage(self.local_chat, "Local")
        
        # Add nearby tab
        self.nearby_chat = wx.richtext.RichTextCtrl(
            self.chat_tabs,
            style=wx.richtext.RE_MULTILINE | wx.richtext.RE_READONLY
        )
        self.chat_tabs.AddPage(self.nearby_chat, "Nearby")
        
        # Add IM tab
        self.im_chat = wx.richtext.RichTextCtrl(
            self.chat_tabs,
            style=wx.richtext.RE_MULTILINE | wx.richtext.RE_READONLY
        )
        self.chat_tabs.AddPage(self.im_chat, "IMs")
        
        # Add group tab
        self.group_chat = wx.richtext.RichTextCtrl(
            self.chat_tabs,
            style=wx.richtext.RE_MULTILINE | wx.richtext.RE_READONLY
        )
        self.chat_tabs.AddPage(self.group_chat, "Groups")
        
        main_sizer.Add(self.chat_tabs, 1, wx.EXPAND | wx.ALL, 5)
        
        # Create input area
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Chat channel selector
        self.channel_label = wx.StaticText(self, label="Channel:")
        self.channel_input = wx.TextCtrl(self, size=(50, -1), value="0")
        input_sizer.Add(self.channel_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        input_sizer.Add(self.channel_input, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        # Input text box
        self.input_text = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        input_sizer.Add(self.input_text, 1, wx.ALIGN_CENTER_VERTICAL)
        
        # Send button
        self.send_button = wx.Button(self, label="Send")
        input_sizer.Add(self.send_button, 0, wx.LEFT, 5)
        
        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Set sizer
        self.SetSizer(main_sizer)
        
    def on_tab_change(self, event):
        """Handle tab change"""
        tab_index = event.GetSelection()
        tab_name = self.chat_tabs.GetPageText(tab_index).lower()
        
        if tab_name == "local":
            self.active_chat = "local"
            self.channel_label.Show()
            self.channel_input.Show()
        elif tab_name == "nearby":
            self.active_chat = "nearby"
            self.channel_label.Hide()
            self.channel_input.Hide()
        elif tab_name == "ims":
            self.active_chat = "im"
            self.channel_label.Hide()
            self.channel_input.Hide()
        elif tab_name == "groups":
            self.active_chat = "group"
            self.channel_label.Hide()
            self.channel_input.Hide()
        
        self.Layout()
        
    def on_send_message(self, event):
        """Handle send message"""
        # Get message text
        message = self.input_text.GetValue().strip()
        
        if not message:
            return
            
        # Process the message
        if self.active_chat == "local":
            channel = self.channel_input.GetValue().strip()
            try:
                channel_num = int(channel)
                self.send_local_chat(message, channel_num)
            except ValueError:
                self.add_system_message("Invalid channel number")
        elif self.active_chat == "nearby":
            self.send_nearby_chat(message)
        elif self.active_chat == "im":
            self.send_im(message)
        elif self.active_chat == "group":
            self.send_group_chat(message)
            
        # Clear input
        self.input_text.SetValue("")
        
    def send_local_chat(self, message, channel=0):
        """Send a message to local chat"""
        if not self.main_window.is_logged_in:
            self.add_system_message("You must be logged in to chat")
            return
            
        # Get user info
        user = self.main_window.user
        display_name = f"{user.first_name} {user.last_name}"
        
        # Add to local chat display
        if channel == 0:
            self.add_chat_message(self.local_chat, display_name, message)
        else:
            self.add_chat_message(
                self.local_chat,
                display_name,
                message,
                f"Channel {channel}"
            )
            
        # TODO: Actually send the message to the server
        self.logger.info(f"Local chat ({channel}): {display_name}: {message}")
        
    def send_nearby_chat(self, message):
        """Send a message to nearby chat"""
        if not self.main_window.is_logged_in:
            self.add_system_message("You must be logged in to chat")
            return
            
        # Get user info
        user = self.main_window.user
        display_name = f"{user.first_name} {user.last_name}"
        
        # Add to nearby chat display
        self.add_chat_message(self.nearby_chat, display_name, message)
            
        # TODO: Actually send the message to the server
        self.logger.info(f"Nearby chat: {display_name}: {message}")
        
    def send_im(self, message):
        """Send an instant message"""
        if not self.main_window.is_logged_in:
            self.add_system_message("You must be logged in to send IMs")
            return
            
        # TODO: Implement IM targeting
        self.add_system_message("IM functionality not yet implemented")
        
    def send_group_chat(self, message):
        """Send a group chat message"""
        if not self.main_window.is_logged_in:
            self.add_system_message("You must be logged in to use group chat")
            return
            
        # TODO: Implement group chat
        self.add_system_message("Group chat functionality not yet implemented")
        
    def add_chat_message(self, text_ctrl, sender, message, suffix=None):
        """Add a chat message to the specified text control"""
        # Get current time
        timestamp = time.strftime("[%H:%M:%S]")
        
        # Format message
        if suffix:
            header = f"{timestamp} {sender} ({suffix}): "
        else:
            header = f"{timestamp} {sender}: "
            
        # Add to control with formatting
        text_ctrl.BeginTextColour(wx.Colour(100, 100, 100))
        text_ctrl.WriteText(timestamp + " ")
        text_ctrl.EndTextColour()
        
        text_ctrl.BeginTextColour(wx.Colour(0, 0, 200))
        text_ctrl.BeginBold()
        text_ctrl.WriteText(sender)
        text_ctrl.EndBold()
        text_ctrl.EndTextColour()
        
        if suffix:
            text_ctrl.BeginTextColour(wx.Colour(100, 100, 100))
            text_ctrl.WriteText(f" ({suffix})")
            text_ctrl.EndTextColour()
            
        text_ctrl.WriteText(": ")
        text_ctrl.WriteText(message)
        text_ctrl.Newline()
        
        # Scroll to bottom
        text_ctrl.ShowPosition(text_ctrl.GetLastPosition())
        
    def add_system_message(self, message):
        """Add a system message to the current chat"""
        # Determine which text control to use
        if self.active_chat == "local":
            text_ctrl = self.local_chat
        elif self.active_chat == "nearby":
            text_ctrl = self.nearby_chat
        elif self.active_chat == "im":
            text_ctrl = self.im_chat
        elif self.active_chat == "group":
            text_ctrl = self.group_chat
        else:
            text_ctrl = self.local_chat
            
        # Get current time
        timestamp = time.strftime("[%H:%M:%S]")
        
        # Add to control with formatting
        text_ctrl.BeginTextColour(wx.Colour(100, 100, 100))
        text_ctrl.WriteText(timestamp + " ")
        text_ctrl.EndTextColour()
        
        text_ctrl.BeginTextColour(wx.Colour(200, 0, 0))
        text_ctrl.BeginBold()
        text_ctrl.WriteText("System")
        text_ctrl.EndBold()
        text_ctrl.EndTextColour()
        
        text_ctrl.WriteText(": ")
        text_ctrl.WriteText(message)
        text_ctrl.Newline()
        
        # Scroll to bottom
        text_ctrl.ShowPosition(text_ctrl.GetLastPosition())
    
    def receive_chat(self, sender_name, message, channel=0):
        """Process received chat message from the grid"""
        if channel == 0:
            self.add_chat_message(self.local_chat, sender_name, message)
        else:
            self.add_chat_message(
                self.local_chat,
                sender_name,
                message,
                f"Channel {channel}"
            )
            
    def receive_im(self, sender_name, message):
        """Process received instant message"""
        # Add to IM display
        self.add_chat_message(self.im_chat, sender_name, message)
        
        # If not currently viewing IMs, highlight the tab
        if self.chat_tabs.GetSelection() != 2:  # IM tab index
            self.chat_tabs.SetPageText(2, "* IMs *")
    
    def on_login_success(self):
        """Handle successful login"""
        # Clear chat displays
        self.local_chat.Clear()
        self.nearby_chat.Clear()
        self.im_chat.Clear()
        self.group_chat.Clear()
        
        # Add welcome message
        self.add_system_message("Welcome to Kitely! You are now connected to the grid.")
        
    def on_logout(self):
        """Handle logout"""
        # Clear chat displays
        self.local_chat.Clear()
        self.nearby_chat.Clear()
        self.im_chat.Clear()
        self.group_chat.Clear()
        
        # Reset tab labels
        self.chat_tabs.SetPageText(2, "IMs")  # Reset IM tab label
