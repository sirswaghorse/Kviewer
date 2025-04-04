"""
Connection class for KitelyView.
Handles network connections to OpenSimulator servers.
"""

import logging
import json
import time
import uuid
import requests
import hashlib

# Import conditionally to avoid errors when dependency is missing
try:
    import websocket
except ImportError:
    websocket = None

from app.network.opensim_protocol import OpenSimProtocol, MessageType
from app.network.packet_handler import PacketHandler

class GridConnection:
    """Handles connection to an OpenSimulator grid"""
    
    def __init__(self, config):
        """Initialize grid connection"""
        self.logger = logging.getLogger("kitelyview")
        self.config = config
        
        # Login information
        self.logged_in = False
        self.session_id = None
        self.circuit_code = None
        self.secure_session_id = None
        self.inventory_root = None
        self.user_data = None
        
        # Region information
        self.current_region = {
            "name": None,
            "handle": None,
            "ip": None,
            "port": None,
            "position": [0, 0, 0]
        }
        
        # Callbacks
        self.callbacks = {
            "chat_message": [],
            "instant_message": [],
            "object_update": [],
            "inventory_update": [],
            "avatar_update": [],
            "region_change": [],
            "teleport": []
        }
        
        # Initialize protocol and packet handler
        self.protocol = OpenSimProtocol()
        self.packet_handler = PacketHandler(self)
        
        self.websocket_connection = None
        
    def login(self, first_name, last_name, password, start_location="last"):
        """Authenticate with the grid"""
        self.logger.info(f"Attempting login for {first_name} {last_name}")
        
        # In a real implementation, we would make actual login requests to the grid
        # For this demo, we'll simulate a successful login
        
        # In a real implementation:
        # - Calculate password hash
        # - Send login request to grid login URI
        # - Parse response
        # - Set up UDP or WebSocket connection to simulator
        
        # Simulate login process
        grid_uri = self.config.get("grid", "login_uri")
        self.logger.info(f"Connecting to grid: {grid_uri}")
        
        # Simulate network request
        time.sleep(0.5)
        
        # For demo purposes, create simulated response
        # In a real client, this would be the response from the login server
        success = True
        user_data = {
            "id": str(uuid.uuid4()),
            "name": f"{first_name} {last_name}",
            "session_id": str(uuid.uuid4()),
            "secure_session_id": str(uuid.uuid4()),
            "circuit_code": 12345678,
            "inventory_root": str(uuid.uuid4()),
            "home_location": "Kitely Plaza/128/128/30",
            "last_location": "Kitely Plaza/128/128/30",
            "currency": 1000,
            "friends": [
                {"id": str(uuid.uuid4()), "name": "Friend One", "online": True},
                {"id": str(uuid.uuid4()), "name": "Friend Two", "online": False}
            ],
            "groups": [
                {"id": str(uuid.uuid4()), "name": "Kitely Explorers", "title": "Member"},
                {"id": str(uuid.uuid4()), "name": "Builders Guild", "title": "Builder"}
            ]
        }
        
        if success:
            self.logged_in = True
            self.session_id = user_data["session_id"]
            self.secure_session_id = user_data["secure_session_id"]
            self.circuit_code = user_data["circuit_code"]
            self.inventory_root = user_data["inventory_root"]
            self.user_data = user_data
            
            # Set up current region from last location or home location
            location = start_location
            if start_location.lower() == "last":
                location = user_data["last_location"]
            elif start_location.lower() == "home":
                location = user_data["home_location"]
                
            self._parse_location(location)
            self._connect_to_simulator()
            
            self.logger.info(f"Login successful. Session ID: {self.session_id}")
            return True, user_data
        else:
            self.logger.error("Login failed")
            return False, "Authentication failed"
    
    def disconnect(self):
        """Close connection to the grid"""
        if not self.logged_in:
            return
        
        self.logger.info("Disconnecting from grid")
        
        # In a real implementation:
        # - Send LogoutRequest message to simulator
        # - Close UDP or WebSocket connection
        
        # Simulate logout
        time.sleep(0.5)
        
        # Close WebSocket connection if open
        if self.websocket_connection:
            try:
                self.websocket_connection.close()
            except Exception as e:
                self.logger.error(f"Error closing WebSocket: {e}")
        
        self.logged_in = False
        self.session_id = None
        self.circuit_code = None
        self.secure_session_id = None
        
        self.logger.info("Disconnected from grid")
    
    def send_chat_message(self, message, channel=0):
        """Send a chat message to the current region"""
        if not self.logged_in:
            self.logger.error("Cannot send chat message: Not logged in")
            return False
        
        self.logger.info(f"Sending chat message on channel {channel}: {message}")
        
        # In a real implementation:
        # - Create ChatFromViewer message
        # - Send message to simulator
        
        # Simulate message sending
        time.sleep(0.1)
        
        # For demo, simulate that message was sent successfully
        return True
    
    def teleport(self, region_name, x, y, z):
        """Teleport to another region"""
        if not self.logged_in:
            self.logger.error("Cannot teleport: Not logged in")
            return False
        
        self.logger.info(f"Requesting teleport to {region_name} at position {x},{y},{z}")
        
        # In a real implementation:
        # - Create TeleportLocationRequest message
        # - Send message to simulator
        # - Wait for teleport confirmation
        # - Handle connecting to new simulator
        
        # Simulate teleport process
        time.sleep(1.0)
        
        # Update current region (simulation)
        self.current_region["name"] = region_name
        self.current_region["position"] = [x, y, z]
        
        # Trigger any teleport callbacks
        for callback in self.callbacks["teleport"]:
            try:
                callback(region_name, x, y, z)
            except Exception as e:
                self.logger.error(f"Error in teleport callback: {e}")
        
        self.logger.info(f"Teleported to {region_name} at position {x},{y},{z}")
        return True
    
    def register_callback(self, event_type, callback):
        """Register a callback for an event type"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            return True
        return False
    
    def unregister_callback(self, event_type, callback):
        """Unregister a callback for an event type"""
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            return True
        return False
    
    def _parse_location(self, location_string):
        """Parse location string into region name and position"""
        try:
            # Format: "RegionName/X/Y/Z"
            parts = location_string.split("/")
            if len(parts) >= 4:
                region_name = parts[0]
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                
                self.current_region["name"] = region_name
                self.current_region["position"] = [x, y, z]
                
                # In a real implementation, we would retrieve additional
                # region data like handle, IP, port from the grid service
            else:
                self.logger.error(f"Invalid location format: {location_string}")
        except Exception as e:
            self.logger.error(f"Error parsing location: {e}")
    
    def _connect_to_simulator(self):
        """Connect to the current region simulator"""
        if not self.logged_in:
            self.logger.error("Cannot connect to simulator: Not logged in")
            return False
        
        region_name = self.current_region["name"]
        self.logger.info(f"Connecting to simulator for region: {region_name}")
        
        # In a real implementation:
        # - Look up simulator host and port from grid
        # - Establish UDP or WebSocket connection
        # - Send UseCircuitCode message
        # - Send CompleteAgentMovement message
        
        # Simulate connection setup
        time.sleep(0.5)
        
        # Simulate setting up region information from grid response
        self.current_region["ip"] = "simulator.kitely.com"
        self.current_region["port"] = 8002
        self.current_region["handle"] = 12345678
        
        # For demo, simulate WebSocket connection
        # In real client, would use either UDP or WebSocket depending on implementation
        websocket_uri = f"wss://{self.current_region['ip']}:{self.current_region['port']}/websocket"
        
        # In a real client we would do:
        # self.websocket_connection = websocket.WebSocketApp(
        #    websocket_uri,
        #    on_message=self._on_websocket_message,
        #    on_error=self._on_websocket_error,
        #    on_close=self._on_websocket_close,
        #    on_open=self._on_websocket_open
        # )
        # websocket_thread = threading.Thread(target=self.websocket_connection.run_forever)
        # websocket_thread.daemon = True
        # websocket_thread.start()
        
        self.logger.info(f"Connected to simulator: {region_name}")
        return True
    
    def _on_websocket_message(self, ws, message):
        """Handle WebSocket message"""
        # In a real implementation, this would parse OpenSim protocol 
        # messages and dispatch them to appropriate handlers
        pass
    
    def _on_websocket_error(self, ws, error):
        """Handle WebSocket error"""
        self.logger.error(f"WebSocket error: {error}")
    
    def _on_websocket_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        self.logger.info(f"WebSocket connection closed: {close_msg} ({close_status_code})")
    
    def _on_websocket_open(self, ws):
        """Handle WebSocket open"""
        self.logger.info("WebSocket connection established")
        # In a real implementation, this would send initial protocol messages