"""
Object models for KitelyView.
Represents in-world objects (prims) and their properties.
"""

import logging
import uuid
from app.utils.vector import Vector3

class ObjectProperties:
    """Properties for an in-world object"""
    
    def __init__(self):
        """Initialize default object properties"""
        # Basic properties
        self.name = "Object"
        self.description = ""
        self.click_action = 0
        self.material = 3  # Default is wood
        
        # Creator info
        self.creator_id = None
        self.owner_id = None
        self.group_id = None
        self.last_owner_id = None
        self.created = 0
        
        # Permissions
        self.base_perm = 0
        self.owner_perm = 0
        self.group_perm = 0
        self.everyone_perm = 0
        self.next_owner_perm = 0
        
        # Physical properties
        self.physical = False
        self.temporary = False
        self.phantom = False
        self.physics_shape_type = 0  # 0 = prim, 1 = convex hull, 2 = mesh
        self.gravity_multiplier = 1.0
        self.friction = 0.5
        self.density = 1000.0  # kg/m^3
        self.restitution = 0.5  # Bounciness
        
        # Media properties
        self.media_url = ""
        
        # Sale info
        self.for_sale = False
        self.sale_price = 0
        self.sale_type = 0  # 0 = not for sale
        
    def update_from_data(self, data):
        """Update properties from server data"""
        # Basic properties
        if "name" in data:
            self.name = data["name"]
            
        if "description" in data:
            self.description = data["description"]
            
        if "click_action" in data:
            self.click_action = data["click_action"]
            
        if "material" in data:
            self.material = data["material"]
            
        # Creator info
        if "creator_id" in data:
            self.creator_id = data["creator_id"]
            
        if "owner_id" in data:
            self.owner_id = data["owner_id"]
            
        if "group_id" in data:
            self.group_id = data["group_id"]
            
        if "last_owner_id" in data:
            self.last_owner_id = data["last_owner_id"]
            
        if "created" in data:
            self.created = data["created"]
            
        # Permissions
        if "base_perm" in data:
            self.base_perm = data["base_perm"]
            
        if "owner_perm" in data:
            self.owner_perm = data["owner_perm"]
            
        if "group_perm" in data:
            self.group_perm = data["group_perm"]
            
        if "everyone_perm" in data:
            self.everyone_perm = data["everyone_perm"]
            
        if "next_owner_perm" in data:
            self.next_owner_perm = data["next_owner_perm"]
            
        # Physical properties
        if "physical" in data:
            self.physical = data["physical"]
            
        if "temporary" in data:
            self.temporary = data["temporary"]
            
        if "phantom" in data:
            self.phantom = data["phantom"]
            
        if "physics_shape_type" in data:
            self.physics_shape_type = data["physics_shape_type"]
            
        if "gravity_multiplier" in data:
            self.gravity_multiplier = data["gravity_multiplier"]
            
        if "friction" in data:
            self.friction = data["friction"]
            
        if "density" in data:
            self.density = data["density"]
            
        if "restitution" in data:
            self.restitution = data["restitution"]
            
        # Media properties
        if "media_url" in data:
            self.media_url = data["media_url"]
            
        # Sale info
        if "for_sale" in data:
            self.for_sale = data["for_sale"]
            
        if "sale_price" in data:
            self.sale_price = data["sale_price"]
            
        if "sale_type" in data:
            self.sale_type = data["sale_type"]
            
    def to_dict(self):
        """Convert properties to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "click_action": self.click_action,
            "material": self.material,
            "creator_id": self.creator_id,
            "owner_id": self.owner_id,
            "group_id": self.group_id,
            "last_owner_id": self.last_owner_id,
            "created": self.created,
            "base_perm": self.base_perm,
            "owner_perm": self.owner_perm,
            "group_perm": self.group_perm,
            "everyone_perm": self.everyone_perm,
            "next_owner_perm": self.next_owner_perm,
            "physical": self.physical,
            "temporary": self.temporary,
            "phantom": self.phantom,
            "physics_shape_type": self.physics_shape_type,
            "gravity_multiplier": self.gravity_multiplier,
            "friction": self.friction,
            "density": self.density,
            "restitution": self.restitution,
            "media_url": self.media_url,
            "for_sale": self.for_sale,
            "sale_price": self.sale_price,
            "sale_type": self.sale_type
        }
        
    def get_material_name(self):
        """Get the name of the material"""
        materials = {
            0: "Stone",
            1: "Metal",
            2: "Glass",
            3: "Wood",
            4: "Flesh",
            5: "Plastic",
            6: "Rubber",
            7: "Light"
        }
        return materials.get(self.material, "Unknown")


class SimObject:
    """Represents an object in the virtual world"""
    
    # Primitive types
    PRIM_BOX = 0
    PRIM_CYLINDER = 1
    PRIM_PRISM = 2
    PRIM_SPHERE = 3
    PRIM_TORUS = 4
    PRIM_TUBE = 5
    PRIM_RING = 6
    PRIM_SCULPT = 7
    PRIM_MESH = 8
    
    def __init__(self, object_id=None, local_id=0):
        """Initialize the simulation object"""
        self.logger = logging.getLogger("kitelyview.models.object")
        
        # Object identification
        self.object_id = object_id or str(uuid.uuid4())
        self.local_id = local_id  # Local ID in the simulator
        self.region_handle = 0    # Region handle
        self.parent_id = 0        # Parent local ID (0 = no parent)
        
        # Transform
        self.position = Vector3(0, 0, 0)
        self.rotation = [0.0, 0.0, 0.0, 1.0]  # Quaternion (x, y, z, w)
        self.scale = Vector3(1, 1, 1)
        self.velocity = Vector3(0, 0, 0)
        self.acceleration = Vector3(0, 0, 0)
        self.angular_velocity = Vector3(0, 0, 0)
        
        # Primitive data
        self.prim_type = self.PRIM_BOX
        self.state = 0  # Object state flags
        self.crc = 0    # CRC for change detection
        
        # Appearance
        self.textures = []  # List of texture IDs for each face
        self.colors = []    # List of colors for each face
        self.alpha = 1.0    # Transparency (1.0 = opaque)
        
        # Properties
        self.properties = ObjectProperties()
        
        # Child prims (if this is a linkset)
        self.children = {}  # Key: local_id, Value: SimObject
        
    def update_from_data(self, data):
        """Update object from server data"""
        try:
            # Update identification
            if "ObjectID" in data:
                self.object_id = data["ObjectID"]
                
            if "LocalID" in data:
                self.local_id = data["LocalID"]
                
            if "RegionHandle" in data:
                self.region_handle = data["RegionHandle"]
                
            if "ParentID" in data:
                self.parent_id = data["ParentID"]
                
            # Update transform
            if "Position" in data:
                pos = data["Position"]
                if isinstance(pos, list) and len(pos) == 3:
                    self.position = Vector3(pos[0], pos[1], pos[2])
                    
            if "Rotation" in data:
                rot = data["Rotation"]
                if isinstance(rot, list) and len(rot) == 4:
                    self.rotation = rot
                    
            if "Scale" in data:
                scale = data["Scale"]
                if isinstance(scale, list) and len(scale) == 3:
                    self.scale = Vector3(scale[0], scale[1], scale[2])
                    
            if "Velocity" in data:
                vel = data["Velocity"]
                if isinstance(vel, list) and len(vel) == 3:
                    self.velocity = Vector3(vel[0], vel[1], vel[2])
                    
            if "Acceleration" in data:
                acc = data["Acceleration"]
                if isinstance(acc, list) and len(acc) == 3:
                    self.acceleration = Vector3(acc[0], acc[1], acc[2])
                    
            if "AngularVelocity" in data:
                ang_vel = data["AngularVelocity"]
                if isinstance(ang_vel, list) and len(ang_vel) == 3:
                    self.angular_velocity = Vector3(ang_vel[0], ang_vel[1], ang_vel[2])
                    
            # Update primitive data
            if "PCode" in data:
                self.prim_type = data["PCode"]
                
            if "State" in data:
                self.state = data["State"]
                
            if "CRC" in data:
                self.crc = data["CRC"]
                
            # Update appearance
            if "Textures" in data:
                self.textures = data["Textures"]
                
            if "Colors" in data:
                self.colors = data["Colors"]
                
            if "Alpha" in data:
                self.alpha = data["Alpha"]
                
            # Update properties
            if "Properties" in data:
                self.properties.update_from_data(data["Properties"])
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating object from data: {e}", exc_info=True)
            return False
            
    def to_dict(self):
        """Convert object to dictionary"""
        return {
            "object_id": self.object_id,
            "local_id": self.local_id,
            "region_handle": self.region_handle,
            "parent_id": self.parent_id,
            "position": [self.position.x, self.position.y, self.position.z],
            "rotation": self.rotation,
            "scale": [self.scale.x, self.scale.y, self.scale.z],
            "velocity": [self.velocity.x, self.velocity.y, self.velocity.z],
            "acceleration": [self.acceleration.x, self.acceleration.y, self.acceleration.z],
            "angular_velocity": [self.angular_velocity.x, self.angular_velocity.y, self.angular_velocity.z],
            "prim_type": self.prim_type,
            "state": self.state,
            "crc": self.crc,
            "textures": self.textures,
            "colors": self.colors,
            "alpha": self.alpha,
            "properties": self.properties.to_dict(),
            "children": {local_id: child.to_dict() for local_id, child in self.children.items()}
        }
        
    def add_child(self, child):
        """Add a child prim to this object"""
        if isinstance(child, SimObject):
            child.parent_id = self.local_id
            self.children[child.local_id] = child
            return True
        return False
        
    def remove_child(self, local_id):
        """Remove a child prim from this object"""
        if local_id in self.children:
            del self.children[local_id]
            return True
        return False
        
    def get_child(self, local_id):
        """Get a child prim by local ID"""
        return self.children.get(local_id)
        
    def get_all_children(self):
        """Get all child prims"""
        return list(self.children.values())
        
    def is_physical(self):
        """Check if the object is physical"""
        return self.properties.physical
        
    def is_phantom(self):
        """Check if the object is phantom (non-colliding)"""
        return self.properties.phantom
        
    def is_temporary(self):
        """Check if the object is temporary"""
        return self.properties.temporary
        
    def get_prim_type_name(self):
        """Get the name of the primitive type"""
        prim_types = {
            self.PRIM_BOX: "Box",
            self.PRIM_CYLINDER: "Cylinder",
            self.PRIM_PRISM: "Prism",
            self.PRIM_SPHERE: "Sphere",
            self.PRIM_TORUS: "Torus",
            self.PRIM_TUBE: "Tube",
            self.PRIM_RING: "Ring",
            self.PRIM_SCULPT: "Sculpt",
            self.PRIM_MESH: "Mesh"
        }
        return prim_types.get(self.prim_type, "Unknown")
