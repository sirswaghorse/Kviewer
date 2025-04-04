"""
GridConnection class for handling connections to OpenSimulator grids.
"""

import os
import sys
import logging
import threading
import time
import requests
import json
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import ssl
import websocket
import queue

from app.network.opensim_protocol import OpenSimProtocol
from app.network.packet_handler import PacketHandler
from app.utils.helpers import get_platform_info, generate_uuid

class GridConnection:
    """Main class for handling grid connections"""
    
    def __init__(self, config):
        """Initialize the grid connection"""
        self.logger = logging.getLogger("kitelyview.network.connection")
        self.logger.info("Initializing grid connection handler")
        
        self.config = config
        self.protocol = OpenSimProtocol()
        self.packet_handler = PacketHandler(self)
        
        # Connection state
        self.connected = False
        self.authenticated = False
        self.session_id = None
        self.secure_session_id = None
        self.agent_id = None
        self.circuit_code = None
        self.seed_capability = None
        
        # Current region info
        self.current_region = None
        self.current_region_handle = None
        
        # Connection details
        self.simulator_address = None
        self.simulator_port = None
        
        # Message queues
        self.send_queue = queue.Queue()
        self.receive_queue = queue.Queue()
        
        # Callback handlers
        self.callbacks = {
            "login_success": [],
            "login_failure": [],
            "disconnected": [],
            "region_handshake": [],
            "chat_message": [],
            "im_message": [],
            "object_update": [],
            "avatar_update": [],
            "inventory_update": []
        }
        
        # Network threads
        self.send_thread = None
        self.receive_thread = None
        self.process_thread = None
        self.running = False
        
        self.logger.info("Grid connection handler initialized")
        
    def login(self, first_name, last_name, password, location="last"):
        """
        Login to the grid
        Returns (success, result) tuple where result is session data or error message
        """
        self.logger.info(f"Attempting login for {first_name} {last_name}")
        
        try:
            # Get login URI from config
            grid_config = self.config.get("grid")
            login_uri = grid_config.get("login_uri", "https://grid.kitely.com:8002")
            
            # Prepare login parameters
            platform_info = get_platform_info()
            channel = "KitelyView"
            version = "0.1.0"
            platform = f"{platform_info['system']} {platform_info['release']}"
            mac = generate_uuid()  # Use a random ID for each login attempt
            
            # Note that in a production viewer, we would use LLSD format
            # but for simplicity in this implementation, we'll use JSON
            
            login_params = {
                "first": first_name,
                "last": last_name,
                "passwd": password,
                "start": location,
                "channel": channel,
                "version": version,
                "platform": platform,
                "mac": mac,
                "id0": "",
                "options": [
                    "inventory-root",
                    "inventory-skeleton",
                    "inventory-lib-root",
                    "inventory-lib-owner",
                    "inventory-skel-lib",
                    "initial-outfit",
                    "event-categories",
                    "event-notifications",
                    "classified-categories",
                    "buddy-list",
                    "ui-config",
                    "login-flags",
                    "global-textures"
                ]
            }
            
            # Send login request
            self.logger.debug(f"Sending login request to {login_uri}")
            
            # Since this is a simplified implementation, we'll use HTTP instead of XMLRPC
            # and we'll bypass the actual login handshake
            # In a real implementation, you would use XMLRPC and follow the OpenSim protocol
            
            # Simulated response for this implementation
            # In a real viewer, you would parse the XMLRPC response
            
            # Fake a brief delay for login process
            time.sleep(1)
            
            # Simulate login response
            response = self._simulate_login_response(first_name, last_name)
            
            # Check if login was successful
            if response.get("login") == "true":
                # Extract session data
                self.session_id = response.get("session_id")
                self.secure_session_id = response.get("secure_session_id")
                self.agent_id = response.get("agent_id")
                self.simulator_address = response.get("sim_ip")
                self.simulator_port = int(response.get("sim_port"))
                self.seed_capability = response.get("seed_capability")
                self.circuit_code = int(response.get("circuit_code"))
                
                # Set connection state
                self.authenticated = True
                
                # Start network threads
                self._start_network_threads()
                
                # Initialize UDP circuit to simulator
                self._init_simulator_connection()
                
                self.logger.info(f"Login successful for {first_name} {last_name}")
                return True, response
            else:
                error_msg = response.get("message", "Unknown login error")
                self.logger.warning(f"Login failed: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            self.logger.error(f"Login error: {e}", exc_info=True)
            return False, f"Error during login: {str(e)}"
            
    def logout(self):
        """Log out from the grid"""
        self.logger.info("Logging out from grid")
        
        if not self.authenticated:
            self.logger.warning("Logout called but not logged in")
            return
            
        try:
            # Send LogoutRequest packet
            # In a real viewer, you would send a proper LogoutRequest UDP packet
            
            # Clean up connection
            self.disconnect()
            
            self.logger.info("Logout completed")
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}", exc_info=True)
            
    def disconnect(self):
        """Disconnect from the grid and clean up"""
        self.logger.info("Disconnecting from grid")
        
        # Stop network threads
        self.running = False
        
        if self.send_thread and self.send_thread.is_alive():
            self.send_thread.join(1)
            
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(1)
            
        if self.process_thread and self.process_thread.is_alive():
            self.process_thread.join(1)
            
        # Clear connection state
        self.connected = False
        self.authenticated = False
        self.session_id = None
        self.secure_session_id = None
        self.agent_id = None
        self.circuit_code = None
        self.seed_capability = None
        self.current_region = None
        self.current_region_handle = None
        self.simulator_address = None
        self.simulator_port = None
        
        # Clear queues
        self._clear_queue(self.send_queue)
        self._clear_queue(self.receive_queue)
        
        self.logger.info("Disconnected from grid")
        
        # Trigger disconnected callbacks
        self._trigger_callback("disconnected")
        
    def _clear_queue(self, q):
        """Clear a queue"""
        try:
            while True:
                q.get_nowait()
                q.task_done()
        except queue.Empty:
            pass
            
    def _start_network_threads(self):
        """Start the network threads"""
        self.logger.info("Starting network threads")
        
        # Set thread control flag
        self.running = True
        
        # Start send thread
        self.send_thread = threading.Thread(
            target=self._send_thread,
            name="OpenSim-SendThread",
            daemon=True
        )
        self.send_thread.start()
        
        # Start receive thread
        self.receive_thread = threading.Thread(
            target=self._receive_thread,
            name="OpenSim-ReceiveThread",
            daemon=True
        )
        self.receive_thread.start()
        
        # Start packet processing thread
        self.process_thread = threading.Thread(
            target=self._process_thread,
            name="OpenSim-ProcessThread",
            daemon=True
        )
        self.process_thread.start()
        
        self.logger.info("Network threads started")
        
    def _send_thread(self):
        """Thread for sending packets to the simulator"""
        self.logger.info("Send thread started")
        
        try:
            while self.running:
                try:
                    # Get packet from queue with timeout
                    packet = self.send_queue.get(timeout=0.1)
                    
                    # In a real viewer, you would send this packet via UDP
                    # For this implementation, we'll just log it
                    self.logger.debug(f"Would send packet: {packet}")
                    
                    # Mark task as done
                    self.send_queue.task_done()
                    
                except queue.Empty:
                    # No packets to send, just continue
                    pass
                    
        except Exception as e:
            self.logger.error(f"Send thread error: {e}", exc_info=True)
            
        self.logger.info("Send thread stopped")
        
    def _receive_thread(self):
        """Thread for receiving packets from the simulator"""
        self.logger.info("Receive thread started")
        
        try:
            while self.running:
                # In a real viewer, you would receive UDP packets here
                # For this implementation, we'll simulate incoming packets periodically
                
                time.sleep(0.5)  # Check for new packets every 500ms
                
                if self.authenticated and self.connected:
                    # Simulate receiving packets
                    self._simulate_incoming_packets()
                    
        except Exception as e:
            self.logger.error(f"Receive thread error: {e}", exc_info=True)
            
        self.logger.info("Receive thread stopped")
        
    def _process_thread(self):
        """Thread for processing received packets"""
        self.logger.info("Process thread started")
        
        try:
            while self.running:
                try:
                    # Get packet from queue with timeout
                    packet = self.receive_queue.get(timeout=0.1)
                    
                    # Process the packet
                    self.packet_handler.handle_packet(packet)
                    
                    # Mark task as done
                    self.receive_queue.task_done()
                    
                except queue.Empty:
                    # No packets to process, just continue
                    pass
                    
        except Exception as e:
            self.logger.error(f"Process thread error: {e}", exc_info=True)
            
        self.logger.info("Process thread stopped")
        
    def _init_simulator_connection(self):
        """Initialize connection to the simulator"""
        self.logger.info(f"Initializing simulator connection to {self.simulator_address}:{self.simulator_port}")
        
        # In a real viewer, you would send UseCircuitCode packet via UDP
        # to establish the circuit with the simulator
        
        # For this implementation, we'll just simulate it
        time.sleep(0.5)  # Simulate network delay
        
        self.connected = True
        self.logger.info("Simulator connection established")
        
    def _simulate_login_response(self, first_name, last_name):
        """Simulate a login response for testing"""
        # This simulates the login response from the grid
        # In a real viewer, this would come from the XMLRPC login request
        
        # Generate some random UUIDs for the session
        session_id = generate_uuid()
        secure_session_id = generate_uuid()
        agent_id = generate_uuid()
        circuit_code = 123456789  # Would be random in real implementation
        
        return {
            "login": "true",
            "first_name": first_name,
            "last_name": last_name,
            "agent_id": agent_id,
            "session_id": session_id,
            "secure_session_id": secure_session_id,
            "circuit_code": str(circuit_code),
            "sim_ip": "127.0.0.1",  # Simulated
            "sim_port": "8002",
            "seed_capability": "https://grid.kitely.com:8002/cap/00000000-0000-0000-0000-000000000000",  # Simulated
            "inventory_root": generate_uuid(),
            "inventory_skeleton": [],
            "inventory_lib_root": generate_uuid(),
            "inventory_lib_owner": generate_uuid(),
            "inventory_skel_lib": [],
            "initial_outfit": [],
            "message": "Welcome to Kitely!",
            "home": "last",
            "look_at": "[0,0,0]",
            "seconds_since_epoch": str(int(time.time())),
            "start_location": "last",
            "agent_access": "M",  # PG/Mature/Adult access
            "max_agent_groups": "42",
            "region_x": "256000",  # Region coordinates
            "region_y": "256000"
        }
        
    def _simulate_incoming_packets(self):
        """Simulate incoming packets for testing"""
        # This is only for the simplified implementation
        # In a real viewer, packets would come from the UDP socket
        
        # Randomly simulate different packet types
        import random
        
        # Only simulate if connected
        if not self.connected or not self.authenticated:
            return
            
        # Simulate various packet types with low probability to avoid flooding
        rand = random.random()
        
        if rand < 0.05:  # 5% chance of simulating an ImprovedTerseObjectUpdate
            packet = {
                "type": "ImprovedTerseObjectUpdate",
                "data": {
                    "RegionData": {
                        "RegionHandle": 123456789,
                        "TimeDilation": 0.9
                    },
                    "ObjectData": {
                        "ID": generate_uuid(),
                        "LocalID": random.randint(1, 10000),
                        "State": 0,
                        "FullID": generate_uuid(),
                        "CRC": random.randint(1, 1000000),
                        "PCode": 9,  # Prim
                        "Material": 3,  # Wood
                        "ClickAction": 0,  # None
                        "Scale": [1.0, 1.0, 1.0],
                        "Position": [
                            128.0 + random.uniform(-10, 10),
                            128.0 + random.uniform(-10, 10),
                            20.0 + random.uniform(0, 10)
                        ],
                        "Rotation": [0.0, 0.0, 0.0, 1.0],
                        "Flags": 0
                    }
                }
            }
            self.receive_queue.put(packet)
            
        elif rand < 0.07:  # 2% chance of simulating a ChatFromSimulator
            packet = {
                "type": "ChatFromSimulator",
                "data": {
                    "FromName": f"User{random.randint(1, 100)}",
                    "SourceID": generate_uuid(),
                    "OwnerID": generate_uuid(),
                    "SourceType": 1,  # Agent
                    "ChatType": 1,  # Normal
                    "Audible": 1,  # Fully audible
                    "Position": [
                        128.0 + random.uniform(-10, 10),
                        128.0 + random.uniform(-10, 10),
                        20.0 + random.uniform(0, 10)
                    ],
                    "Message": f"Hello from the simulator! Random message {random.randint(1, 1000)}",
                    "Time": int(time.time())
                }
            }
            self.receive_queue.put(packet)
            
        elif rand < 0.08:  # 1% chance of simulating an AvatarAnimation
            packet = {
                "type": "AvatarAnimation",
                "data": {
                    "Sender": generate_uuid(),
                    "AnimID": [generate_uuid()],  # Would be actual animation IDs in real viewer
                    "AnimSequenceID": [random.randint(1, 100)]
                }
            }
            self.receive_queue.put(packet)
            
    def register_callback(self, event_type, callback):
        """Register a callback for a specific event"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            return True
        return False
        
    def unregister_callback(self, event_type, callback):
        """Unregister a callback"""
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            return True
        return False
        
    def _trigger_callback(self, event_type, *args, **kwargs):
        """Trigger callbacks for an event"""
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error in {event_type} callback: {e}", exc_info=True)
