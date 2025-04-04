"""
Packet handler for processing OpenSimulator protocol packets.
"""

import logging
import time
import threading
import queue

class PacketHandler:
    """Handler for processing OpenSimulator packets"""
    
    def __init__(self, connection):
        """Initialize the packet handler"""
        self.logger = logging.getLogger("kitelyview.network.packet_handler")
        self.logger.info("Initializing packet handler")
        
        # Store reference to the connection
        self.connection = connection
        
        # Set up packet handlers
        self._init_packet_handlers()
        
        self.logger.info("Packet handler initialized")
        
    def _init_packet_handlers(self):
        """Initialize packet handler functions"""
        # Map message types to handler functions
        from app.network.opensim_protocol import MessageType
        
        self.handlers = {
            MessageType.ChatFromSimulator: self._handle_chat_from_simulator,
            MessageType.ImprovedInstantMessage: self._handle_instant_message,
            MessageType.ImprovedTerseObjectUpdate: self._handle_object_update,
            MessageType.AvatarAnimation: self._handle_avatar_animation,
            MessageType.LayerData: self._handle_layer_data,
            MessageType.RegionHandshake: self._handle_region_handshake,
            MessageType.SimStats: self._handle_sim_stats,
            MessageType.AgentMovementComplete: self._handle_agent_movement_complete,
            MessageType.InventoryFolder: self._handle_inventory_folder,
            MessageType.InventoryItem: self._handle_inventory_item,
            MessageType.ImageData: self._handle_image_data
        }
        
    def handle_packet(self, packet):
        """Process a packet"""
        try:
            # Parse the packet
            message_type, data = self.connection.protocol.parse_packet(packet)
            
            if message_type is None:
                self.logger.warning("Failed to parse packet")
                return
                
            # Find and call the appropriate handler
            handler = self.handlers.get(message_type)
            if handler:
                handler(data)
            else:
                self.logger.debug(f"No handler for message type: {message_type}")
                
        except Exception as e:
            self.logger.error(f"Error handling packet: {e}", exc_info=True)
            
    def _handle_chat_from_simulator(self, data):
        """Handle chat message from simulator"""
        self.logger.debug(f"Chat from simulator: {data}")
        
        # Extract chat data
        from_name = data.get("FromName", "Unknown")
        message = data.get("Message", "")
        chat_type = data.get("ChatType", 1)  # 1 = Normal
        source_type = data.get("SourceType", 1)  # 1 = Agent
        
        # Trigger chat message callback
        self.connection._trigger_callback(
            "chat_message",
            from_name,
            message,
            chat_type,
            source_type
        )
        
    def _handle_instant_message(self, data):
        """Handle instant message"""
        self.logger.debug(f"Instant message: {data}")
        
        # Extract IM data
        from_name = data.get("FromAgentName", "Unknown")
        message = data.get("Message", "")
        im_session_id = data.get("IMSessionID", "")
        
        # Trigger IM message callback
        self.connection._trigger_callback(
            "im_message",
            from_name,
            message,
            im_session_id
        )
        
    def _handle_object_update(self, data):
        """Handle object update"""
        self.logger.debug(f"Object update: {data}")
        
        # Extract object data
        region_data = data.get("RegionData", {})
        object_data = data.get("ObjectData", {})
        
        # Trigger object update callback
        self.connection._trigger_callback(
            "object_update",
            region_data,
            object_data
        )
        
    def _handle_avatar_animation(self, data):
        """Handle avatar animation"""
        self.logger.debug(f"Avatar animation: {data}")
        
        # Extract animation data
        sender = data.get("Sender", "")
        anim_ids = data.get("AnimID", [])
        anim_sequence_ids = data.get("AnimSequenceID", [])
        
        # Trigger avatar update callback
        self.connection._trigger_callback(
            "avatar_update",
            sender,
            anim_ids,
            anim_sequence_ids
        )
        
    def _handle_layer_data(self, data):
        """Handle layer data (terrain, etc)"""
        self.logger.debug(f"Layer data: {data}")
        
        # Extract layer data
        layer_type = data.get("LayerType", 0)
        layer_id = data.get("LayerID", 0)
        layer_data = data.get("Data", bytes())
        
        # Process different layer types
        if layer_type == 0:  # Land
            # Trigger terrain update callback
            self.connection._trigger_callback(
                "terrain_update",
                layer_id,
                layer_data
            )
        elif layer_type == 1:  # Wind
            # Trigger wind update callback
            self.connection._trigger_callback(
                "wind_update",
                layer_id,
                layer_data
            )
        elif layer_type == 2:  # Cloud
            # Trigger cloud update callback
            self.connection._trigger_callback(
                "cloud_update",
                layer_id,
                layer_data
            )
            
    def _handle_region_handshake(self, data):
        """Handle region handshake"""
        self.logger.debug(f"Region handshake: {data}")
        
        # Extract region data
        region_flags = data.get("RegionFlags", 0)
        sim_access = data.get("SimAccess", 0)
        region_name = data.get("SimName", "Unknown")
        region_owner = data.get("SimOwner", "")
        terrain_base0 = data.get("TerrainBase0", 0.0)
        terrain_base1 = data.get("TerrainBase1", 0.0)
        terrain_base2 = data.get("TerrainBase2", 0.0)
        terrain_base3 = data.get("TerrainBase3", 0.0)
        
        # Store region info
        self.connection.current_region = region_name
        
        # Trigger region handshake callback
        self.connection._trigger_callback(
            "region_handshake",
            region_name,
            region_flags,
            sim_access,
            region_owner
        )
        
        # Send RegionHandshakeReply
        # In a real viewer, you would send a proper UDP packet
        
    def _handle_sim_stats(self, data):
        """Handle simulator statistics"""
        self.logger.debug(f"Simulator stats: {data}")
        
        # Extract stats data
        stats = data.get("Statistics", {})
        
        # Trigger simulator stats callback
        self.connection._trigger_callback(
            "simulator_stats",
            stats
        )
        
    def _handle_agent_movement_complete(self, data):
        """Handle agent movement completion"""
        self.logger.debug(f"Agent movement complete: {data}")
        
        # Extract position data
        position = data.get("Position", [0, 0, 0])
        look_at = data.get("LookAt", [0, 0, 0])
        
        # Trigger movement complete callback
        self.connection._trigger_callback(
            "movement_complete",
            position,
            look_at
        )
        
    def _handle_inventory_folder(self, data):
        """Handle inventory folder update"""
        self.logger.debug(f"Inventory folder: {data}")
        
        # Extract folder data
        folder_id = data.get("FolderID", "")
        parent_id = data.get("ParentID", "")
        folder_name = data.get("Name", "")
        
        # Trigger inventory update callback
        self.connection._trigger_callback(
            "inventory_update",
            "folder",
            folder_id,
            parent_id,
            folder_name
        )
        
    def _handle_inventory_item(self, data):
        """Handle inventory item update"""
        self.logger.debug(f"Inventory item: {data}")
        
        # Extract item data
        item_id = data.get("ItemID", "")
        folder_id = data.get("FolderID", "")
        creator_id = data.get("CreatorID", "")
        asset_id = data.get("AssetID", "")
        item_name = data.get("Name", "")
        description = data.get("Description", "")
        
        # Trigger inventory update callback
        self.connection._trigger_callback(
            "inventory_update",
            "item",
            item_id,
            folder_id,
            creator_id,
            asset_id,
            item_name,
            description
        )
        
    def _handle_image_data(self, data):
        """Handle image data (textures)"""
        self.logger.debug(f"Image data: {data}")
        
        # Extract image data
        image_id = data.get("ImageID", "")
        image_data = data.get("Data", bytes())
        image_size = data.get("Size", 0)
        image_packet = data.get("Packet", 0)
        image_packets = data.get("Packets", 0)
        
        # Trigger texture update callback
        self.connection._trigger_callback(
            "texture_update",
            image_id,
            image_data,
            image_size,
            image_packet,
            image_packets
        )
