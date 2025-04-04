"""
User model for KitelyView.
Represents a user account in the OpenSimulator grid.
"""

class User:
    """Represents a user in the virtual world"""
    
    def __init__(self, user_id=None, name=None):
        """Initialize user with ID and name"""
        self.user_id = user_id
        self.name = name
        
        # Personal information
        self.first_name = None
        self.last_name = None
        self.display_name = None
        self.email = None
        
        # Status information
        self.online = False
        self.last_login = None
        self.created_date = None
        
        # Social information
        self.friends = {}  # Dict of {friend_id: {"name": name, "online": bool}}
        self.groups = {}   # Dict of {group_id: {"name": name, "title": title}}
        
        # Current region/position information
        self.current_region_id = None
        
        # Parse name into first_name and last_name if provided
        if name:
            name_parts = name.split(" ", 1)
            if len(name_parts) > 0:
                self.first_name = name_parts[0]
            if len(name_parts) > 1:
                self.last_name = name_parts[1]
    
    def get_full_name(self):
        """Get the user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.name
    
    def get_display_name(self):
        """Get the user's display name, falling back to regular name if not set"""
        if self.display_name:
            return self.display_name
        return self.get_full_name()
    
    def set_online_status(self, status):
        """Set the user's online status"""
        self.online = status
    
    def add_friend(self, friend_id, friend_name):
        """Add a friend to the user's friend list"""
        self.friends[friend_id] = {
            "name": friend_name,
            "online": False
        }
    
    def remove_friend(self, friend_id):
        """Remove a friend from the user's friend list"""
        if friend_id in self.friends:
            del self.friends[friend_id]
    
    def update_friend_status(self, friend_id, online):
        """Update a friend's online status"""
        if friend_id in self.friends:
            self.friends[friend_id]["online"] = online
    
    def add_group(self, group_id, group_name):
        """Add a group to the user's group list"""
        self.groups[group_id] = {
            "name": group_name,
            "title": "Member"  # Default title
        }
    
    def remove_group(self, group_id):
        """Remove a group from the user's group list"""
        if group_id in self.groups:
            del self.groups[group_id]
    
    def update_from_data(self, data):
        """Update user data from server response"""
        if "user_id" in data:
            self.user_id = data["user_id"]
        
        if "name" in data:
            self.name = data["name"]
            name_parts = self.name.split(" ", 1)
            if len(name_parts) > 0:
                self.first_name = name_parts[0]
            if len(name_parts) > 1:
                self.last_name = name_parts[1]
        
        if "display_name" in data:
            self.display_name = data["display_name"]
        
        if "email" in data:
            self.email = data["email"]
        
        if "online" in data:
            self.online = data["online"]
        
        if "last_login" in data:
            self.last_login = data["last_login"]
        
        if "created_date" in data:
            self.created_date = data["created_date"]
        
        if "current_region_id" in data:
            self.current_region_id = data["current_region_id"]
        
        if "friends" in data:
            # Update friends from data
            for friend in data["friends"]:
                friend_id = friend.get("id")
                if friend_id:
                    self.friends[friend_id] = {
                        "name": friend.get("name", "Unknown"),
                        "online": friend.get("online", False)
                    }
        
        if "groups" in data:
            # Update groups from data
            for group in data["groups"]:
                group_id = group.get("id")
                if group_id:
                    self.groups[group_id] = {
                        "name": group.get("name", "Unknown Group"),
                        "title": group.get("title", "Member")
                    }
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name,
            "email": self.email,
            "online": self.online,
            "last_login": self.last_login,
            "created_date": self.created_date,
            "current_region_id": self.current_region_id,
            "friends": [
                {
                    "id": friend_id,
                    "name": friend_data["name"],
                    "online": friend_data["online"]
                }
                for friend_id, friend_data in self.friends.items()
            ],
            "groups": [
                {
                    "id": group_id,
                    "name": group_data["name"],
                    "title": group_data["title"]
                }
                for group_id, group_data in self.groups.items()
            ]
        }