"""
Avatar model for KitelyView.
Represents avatar appearance and animation data.
"""

import logging
import uuid
from app.utils.vector import Vector3

class AvatarAppearance:
    """Stores avatar appearance parameters"""
    
    def __init__(self):
        """Initialize default appearance"""
        # Visual parameters
        self.height = 1.8        # Avatar height in meters
        self.body_type = 0       # 0 = female, 1 = male
        self.skin_color = [0.9, 0.75, 0.65, 1.0]  # RGBA
        self.hair_color = [0.5, 0.3, 0.2, 1.0]   # RGBA
        
        # Body parameters (0.0-1.0 range)
        self.shape_params = {
            # Head shape
            "head_size": 0.5,
            "head_length": 0.5,
            "face_shape": 0.5,
            "eye_size": 0.5,
            "eye_spacing": 0.5,
            "ear_size": 0.5,
            "ear_angle": 0.5,
            "nose_size": 0.5,
            "nose_length": 0.5,
            "mouth_size": 0.5,
            "lip_thickness": 0.5,
            "chin_angle": 0.5,
            "jaw_shape": 0.5,
            
            # Torso
            "torso_length": 0.5,
            "shoulder_width": 0.5,
            "chest_size": 0.5,
            "waist_size": 0.5,
            "hip_width": 0.5,
            
            # Legs
            "leg_length": 0.5,
            "leg_muscles": 0.5,
            "foot_size": 0.5,
            
            # Arms
            "arm_length": 0.5,
            "arm_muscles": 0.5,
            "hand_size": 0.5
        }
        
        # Textures and clothing
        self.skin_texture_id = None
        self.hair_texture_id = None
        self.eye_texture_id = None
        
        # Worn items (UUID of inventory items)
        self.worn_items = {
            "hair": None,
            "eyes": None,
            "shirt": None,
            "pants": None,
            "shoes": None,
            "socks": None,
            "jacket": None,
            "gloves": None,
            "undershirt": None,
            "underpants": None,
            "skirt": None,
            "alpha": None,
            "tattoo": None,
            "physics": None,
            "universal": None
        }
        
        # Attachments (UUID of inventory items and attachment point)
        self.attachments = {}  # Key: attachment point, Value: UUID
        
    def from_dict(self, data):
        """Load appearance from dictionary"""
        if "height" in data:
            self.height = data["height"]
            
        if "body_type" in data:
            self.body_type = data["body_type"]
            
        if "skin_color" in data:
            self.skin_color = data["skin_color"]
            
        if "hair_color" in data:
            self.hair_color = data["hair_color"]
            
        # Update shape parameters
        if "shape_params" in data:
            for key, value in data["shape_params"].items():
                if key in self.shape_params:
                    self.shape_params[key] = value
                    
        # Update textures
        if "skin_texture_id" in data:
            self.skin_texture_id = data["skin_texture_id"]
            
        if "hair_texture_id" in data:
            self.hair_texture_id = data["hair_texture_id"]
            
        if "eye_texture_id" in data:
            self.eye_texture_id = data["eye_texture_id"]
            
        # Update worn items
        if "worn_items" in data:
            for item_type, item_id in data["worn_items"].items():
                if item_type in self.worn_items:
                    self.worn_items[item_type] = item_id
                    
        # Update attachments
        if "attachments" in data:
            self.attachments = data["attachments"]
            
    def to_dict(self):
        """Convert appearance to dictionary"""
        return {
            "height": self.height,
            "body_type": self.body_type,
            "skin_color": self.skin_color,
            "hair_color": self.hair_color,
            "shape_params": self.shape_params,
            "skin_texture_id": self.skin_texture_id,
            "hair_texture_id": self.hair_texture_id,
            "eye_texture_id": self.eye_texture_id,
            "worn_items": self.worn_items,
            "attachments": self.attachments
        }


class Avatar:
    """Represents an avatar in the virtual world"""
    
    def __init__(self, avatar_id=None, name=None):
        """Initialize avatar with optional ID and name"""
        self.logger = logging.getLogger("kitelyview.models.avatar")
        
        # Avatar identification
        self.avatar_id = avatar_id or str(uuid.uuid4())
        self.name = name or "Unknown Avatar"
        self.display_name = None
        
        # Position and orientation
        self.position = Vector3(128, 20, 128)  # Default to region center
        self.rotation = [0.0, 0.0, 0.0, 1.0]  # Quaternion (x, y, z, w)
        self.velocity = Vector3(0, 0, 0)
        self.angular_velocity = Vector3(0, 0, 0)
        
        # State flags
        self.is_flying = False
        self.is_sitting = False
        self.is_typing = False
        self.is_away = False
        
        # Current animation state
        self.current_animation = "stand"  # Default pose
        self.animations = []  # List of currently active animations
        
        # Appearance
        self.appearance = AvatarAppearance()
        
        # Group data
        self.active_group = None
        self.active_group_title = None
        
        # Other metadata
        self.created = None
        self.last_login = None
        self.partner_id = None
        
    def update_from_data(self, data):
        """Update avatar from server data"""
        try:
            # Update identification
            if "avatar_id" in data:
                self.avatar_id = data["avatar_id"]
                
            if "name" in data:
                self.name = data["name"]
                
            if "display_name" in data:
                self.display_name = data["display_name"]
                
            # Update position and orientation
            if "position" in data:
                pos = data["position"]
                if isinstance(pos, list) and len(pos) == 3:
                    self.position = Vector3(pos[0], pos[1], pos[2])
                    
            if "rotation" in data:
                rot = data["rotation"]
                if isinstance(rot, list) and len(rot) == 4:
                    self.rotation = rot
                    
            if "velocity" in data:
                vel = data["velocity"]
                if isinstance(vel, list) and len(vel) == 3:
                    self.velocity = Vector3(vel[0], vel[1], vel[2])
                    
            # Update state flags
            if "is_flying" in data:
                self.is_flying = data["is_flying"]
                
            if "is_sitting" in data:
                self.is_sitting = data["is_sitting"]
                
            if "is_typing" in data:
                self.is_typing = data["is_typing"]
                
            if "is_away" in data:
                self.is_away = data["is_away"]
                
            # Update animations
            if "current_animation" in data:
                self.current_animation = data["current_animation"]
                
            if "animations" in data:
                self.animations = data["animations"]
                
            # Update appearance
            if "appearance" in data:
                self.appearance.from_dict(data["appearance"])
                
            # Update group data
            if "active_group" in data:
                self.active_group = data["active_group"]
                
            if "active_group_title" in data:
                self.active_group_title = data["active_group_title"]
                
            # Update metadata
            if "created" in data:
                self.created = data["created"]
                
            if "last_login" in data:
                self.last_login = data["last_login"]
                
            if "partner_id" in data:
                self.partner_id = data["partner_id"]
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating avatar from data: {e}", exc_info=True)
            return False
            
    def to_dict(self):
        """Convert avatar to dictionary"""
        return {
            "avatar_id": self.avatar_id,
            "name": self.name,
            "display_name": self.display_name,
            "position": [self.position.x, self.position.y, self.position.z],
            "rotation": self.rotation,
            "velocity": [self.velocity.x, self.velocity.y, self.velocity.z],
            "is_flying": self.is_flying,
            "is_sitting": self.is_sitting,
            "is_typing": self.is_typing,
            "is_away": self.is_away,
            "current_animation": self.current_animation,
            "animations": self.animations,
            "appearance": self.appearance.to_dict(),
            "active_group": self.active_group,
            "active_group_title": self.active_group_title,
            "created": self.created,
            "last_login": self.last_login,
            "partner_id": self.partner_id
        }
        
    def get_display_name(self):
        """Get the display name or fall back to avatar name"""
        return self.display_name or self.name
        
    def get_animation_state(self):
        """Get current animation state as a string"""
        if self.is_flying:
            return "flying"
        elif self.is_sitting:
            return "sitting"
        else:
            # Determine if moving based on velocity
            speed = self.velocity.length()
            if speed > 0.1:
                if speed > 5.0:
                    return "running"
                else:
                    return "walking"
            else:
                if self.is_away:
                    return "away"
                elif self.is_typing:
                    return "typing"
                else:
                    return "standing"
