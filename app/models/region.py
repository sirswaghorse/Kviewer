"""
Region models for KitelyView.
Represents OpenSimulator regions and their properties.
"""

import logging
import uuid

class RegionInfo:
    """Information about a region/simulator"""
    
    def __init__(self):
        """Initialize default region info"""
        # Region identification
        self.region_id = None
        self.region_name = "Unknown Region"
        self.region_handle = 0
        
        # Region coordinates in grid
        self.region_x = 0
        self.region_y = 0
        
        # Region size
        self.size_x = 256
        self.size_y = 256
        
        # Owner information
        self.owner_id = None
        self.owner_name = None
        
        # Access settings
        self.access_flags = 0  # Region access flags
        self.access_level = 0  # PG/Mature/Adult
        
        # Technical information
        self.server_uri = None
        self.server_ip = None
        self.server_port = 0
        self.http_port = 0
        self.internal_port = 0
        
        # Region status
        self.online = False
        
    def update_from_data(self, data):
        """Update region info from server data"""
        # Region identification
        if "region_id" in data:
            self.region_id = data["region_id"]
            
        if "region_name" in data:
            self.region_name = data["region_name"]
            
        if "region_handle" in data:
            self.region_handle = data["region_handle"]
            
        # Region coordinates
        if "region_x" in data:
            self.region_x = data["region_x"]
            
        if "region_y" in data:
            self.region_y = data["region_y"]
            
        # Region size
        if "size_x" in data:
            self.size_x = data["size_x"]
            
        if "size_y" in data:
            self.size_y = data["size_y"]
            
        # Owner information
        if "owner_id" in data:
            self.owner_id = data["owner_id"]
            
        if "owner_name" in data:
            self.owner_name = data["owner_name"]
            
        # Access settings
        if "access_flags" in data:
            self.access_flags = data["access_flags"]
            
        if "access_level" in data:
            self.access_level = data["access_level"]
            
        # Technical information
        if "server_uri" in data:
            self.server_uri = data["server_uri"]
            
        if "server_ip" in data:
            self.server_ip = data["server_ip"]
            
        if "server_port" in data:
            self.server_port = data["server_port"]
            
        if "http_port" in data:
            self.http_port = data["http_port"]
            
        if "internal_port" in data:
            self.internal_port = data["internal_port"]
            
        # Region status
        if "online" in data:
            self.online = data["online"]
            
    def to_dict(self):
        """Convert region info to dictionary"""
        return {
            "region_id": self.region_id,
            "region_name": self.region_name,
            "region_handle": self.region_handle,
            "region_x": self.region_x,
            "region_y": self.region_y,
            "size_x": self.size_x,
            "size_y": self.size_y,
            "owner_id": self.owner_id,
            "owner_name": self.owner_name,
            "access_flags": self.access_flags,
            "access_level": self.access_level,
            "server_uri": self.server_uri,
            "server_ip": self.server_ip,
            "server_port": self.server_port,
            "http_port": self.http_port,
            "internal_port": self.internal_port,
            "online": self.online
        }
        
    def get_access_level_name(self):
        """Get the name of the access level"""
        access_levels = {
            0: "PG",
            1: "Mature",
            2: "Adult"
        }
        return access_levels.get(self.access_level, "Unknown")


class Region:
    """Represents an OpenSimulator region"""
    
    def __init__(self, region_id=None, region_name="Unknown Region"):
        """Initialize the region"""
        self.logger = logging.getLogger("kitelyview.models.region")
        
        # Region information
        self.info = RegionInfo()
        self.info.region_id = region_id or str(uuid.uuid4())
        self.info.region_name = region_name
        
        # Region content
        self.terrain_heightmap = None
        self.water_height = 20.0
        
        # Parcel data
        self.parcels = {}  # Key: parcel_id, Value: Parcel object
        
        # Environment data
        self.sky_settings = {
            "ambient": [0.25, 0.25, 0.25, 1.0],
            "blue_density": [0.2, 0.2, 0.8, 1.0],
            "blue_horizon": [0.5, 0.5, 0.8, 1.0],
            "cloud_color": [0.5, 0.5, 0.5, 1.0],
            "cloud_coverage": 0.5,
            "cloud_scale": 0.42,
            "density_multiplier": 1.0,
            "distance_multiplier": 1.0,
            "haze_density": 0.7,
            "haze_horizon": 0.19,
            "sun_glow_focus": 0.1,
            "sun_glow_size": 1.0,
            "sun_moon_color": [1.0, 1.0, 1.0, 1.0]
        }
        
        self.water_settings = {
            "color": [0.12, 0.22, 0.25, 0.7],
            "fog_color": [0.12, 0.22, 0.25, 0.7],
            "fog_density": 2.0,
            "fresnel_scale": 0.4,
            "fresnel_offset": 0.5,
            "wave1_direction": [0.7, 0.7],
            "wave2_direction": [0.7, 0.7]
        }
        
        # Windlight settings
        self.windlight = {
            "preset_name": "Default",
            "use_region_settings": True
        }
        
    def update_from_data(self, data):
        """Update region from server data"""
        try:
            # Update region info
            if "info" in data:
                self.info.update_from_data(data["info"])
                
            # Update terrain
            if "terrain_heightmap" in data:
                self.terrain_heightmap = data["terrain_heightmap"]
                
            if "water_height" in data:
                self.water_height = data["water_height"]
                
            # Update environment
            if "sky_settings" in data:
                self.sky_settings.update(data["sky_settings"])
                
            if "water_settings" in data:
                self.water_settings.update(data["water_settings"])
                
            if "windlight" in data:
                self.windlight.update(data["windlight"])
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating region from data: {e}", exc_info=True)
            return False
            
    def to_dict(self):
        """Convert region to dictionary"""
        return {
            "info": self.info.to_dict(),
            "water_height": self.water_height,
            "sky_settings": self.sky_settings,
            "water_settings": self.water_settings,
            "windlight": self.windlight,
            "parcels": {parcel_id: parcel.to_dict() for parcel_id, parcel in self.parcels.items()}
        }
        
    def add_parcel(self, parcel):
        """Add a parcel to this region"""
        from app.models.parcel import Parcel
        if isinstance(parcel, Parcel):
            self.parcels[parcel.parcel_id] = parcel
            return True
        return False
        
    def remove_parcel(self, parcel_id):
        """Remove a parcel from this region"""
        if parcel_id in self.parcels:
            del self.parcels[parcel_id]
            return True
        return False
        
    def get_parcel(self, parcel_id):
        """Get a parcel by ID"""
        return self.parcels.get(parcel_id)
        
    def get_all_parcels(self):
        """Get all parcels in this region"""
        return list(self.parcels.values())
        
    def get_terrain_height(self, x, y):
        """Get terrain height at the specified coordinates"""
        if self.terrain_heightmap is None:
            return 0.0
            
        try:
            # Convert global coordinates to heightmap indices
            x_idx = int(x) % self.info.size_x
            y_idx = int(y) % self.info.size_y
            
            return self.terrain_heightmap[x_idx, y_idx]
        except Exception as e:
            self.logger.error(f"Error getting terrain height: {e}", exc_info=True)
            return 0.0
            
    def is_water_height(self, height):
        """Check if the given height is at or below water level"""
        return height <= self.water_height
