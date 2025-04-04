"""
User model for KitelyView.
Represents the logged-in user's identity and session data.
"""

import logging
import time

class User:
    """Represents a logged-in user in the OpenSimulator grid"""
    
    def __init__(self, data=None):
        """Initialize user object with optional data"""
        self.logger = logging.getLogger("kitelyview.models.user")
        
        # User identification
        self.first_name = "Guest"
        self.last_name = "User"
        self.display_name = None
        self.agent_id = None
        
        # Session data
        self.session_id = None
        self.secure_session_id = None
        self.circuit_code = None
        self.start_location = "last"
        self.home_location = None
        
        # Grid access
        self.access_level = "M"  # PG/Mature/Adult
        self.max_agent_groups = 42
        
        # Login info
        self.logged_in = False
        self.login_time = None
        self.last_region = None
        
        # Inventory root folders
        self.inventory_root = None
        self.library_root = None
        self.library_owner = None
        
        # Update with provided data
        if data:
            self.update_from_data(data)
            
    def update_from_data(self, data):
        """Update user from login response data"""
        # Basic identification
        if "first_name" in data:
            self.first_name = data["first_name"]
            
        if "last_name" in data:
            self.last_name = data["last_name"]
            
        if "display_name" in data:
            self.display_name = data["display_name"]
            
        if "agent_id" in data:
            self.agent_id = data["agent_id"]
            
        # Session data
        if "session_id" in data:
            self.session_id = data["session_id"]
            
        if "secure_session_id" in data:
            self.secure_session_id = data["secure_session_id"]
            
        if "circuit_code" in data:
            if isinstance(data["circuit_code"], str):
                self.circuit_code = int(data["circuit_code"])
            else:
                self.circuit_code = data["circuit_code"]
                
        if "start_location" in data:
            self.start_location = data["start_location"]
            
        if "home" in data:
            self.home_location = data["home"]
            
        # Grid access
        if "agent_access" in data:
            self.access_level = data["agent_access"]
            
        if "max_agent_groups" in data:
            if isinstance(data["max_agent_groups"], str):
                self.max_agent_groups = int(data["max_agent_groups"])
            else:
                self.max_agent_groups = data["max_agent_groups"]
                
        # Inventory root folders
        if "inventory_root" in data:
            self.inventory_root = data["inventory_root"]
            
        if "inventory_lib_root" in data:
            self.library_root = data["inventory_lib_root"]
            
        if "inventory_lib_owner" in data:
            self.library_owner = data["inventory_lib_owner"]
            
        # Set login state
        if "login" in data and data["login"] == "true":
            self.logged_in = True
            self.login_time = time.time()
            
        # Log success
        self.logger.info(f"Updated user data for {self.first_name} {self.last_name}")
            
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
        
    def get_display_name(self):
        """Get user's display name or full name if no display name"""
        return self.display_name or self.get_full_name()
        
    def is_logged_in(self):
        """Check if user is logged in"""
        return self.logged_in and self.session_id is not None
        
    def can_access_mature(self):
        """Check if user can access mature content"""
        return self.access_level in ['M', 'A']
        
    def can_access_adult(self):
        """Check if user can access adult content"""
        return self.access_level == 'A'
        
    def logout(self):
        """Log out the user"""
        self.logged_in = False
        self.session_id = None
        self.secure_session_id = None
        self.circuit_code = None
        
        self.logger.info(f"Logged out user {self.first_name} {self.last_name}")
        
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "secure_session_id": self.secure_session_id,
            "circuit_code": self.circuit_code,
            "start_location": self.start_location,
            "home_location": self.home_location,
            "access_level": self.access_level,
            "max_agent_groups": self.max_agent_groups,
            "logged_in": self.logged_in,
            "login_time": self.login_time,
            "last_region": self.last_region,
            "inventory_root": self.inventory_root,
            "library_root": self.library_root,
            "library_owner": self.library_owner
        }
