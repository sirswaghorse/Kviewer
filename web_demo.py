#!/usr/bin/env python3
"""
KitelyView Web Demo - A web-based demonstration of the KitelyView application.
This script provides a web interface to visualize the simulation with 3D capabilities.
"""

import sys
import os
import logging
import time
import json
import threading
import queue
import random
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

from app.utils.logger import setup_logger
from app.config import Config
from app.models.user import User
from app.models.inventory import InventoryFolder, InventoryItem
from app.network.connection import GridConnection

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kitelyview-demo-secret'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for simulation state
simulation_events = queue.Queue()
simulation_state = {
    "logged_in": False,
    "user": None,
    "current_region": None,
    "position": [0, 0, 0],
    "chat_messages": [],
    "inventory": {
        "root": {
            "name": "My Inventory", 
            "items": []
        }
    },
    "status": "idle",
    "avatar_appearance": {
        "height": 1.0,
        "bodyShape": "athletic",
        "skinColor": "#f2d2bd",
        "hairStyle": "short",
        "hairColor": "#523b22",
        "outfitStyle": "casual",
        "outfitPrimaryColor": "#3f51b5",
        "outfitSecondaryColor": "#f44336"
    },
    "objects": []
}

# Custom log handler to capture log events for the web interface
class WebLogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        event_type = "log"
        
        # Detect special event types from the message
        if "CHAT:" in msg:
            event_type = "chat"
            msg = msg.split("CHAT: ")[1]
        elif "TELEPORT:" in msg:
            event_type = "teleport"
            msg = msg.split("TELEPORT: ")[1]
        elif "Login successful" in msg and "user" in msg:
            event_type = "login"
        elif "Disconnected from grid" in msg:
            event_type = "logout"
            
        simulation_events.put({
            "type": event_type,
            "message": msg,
            "timestamp": time.time(),
            "level": record.levelname
        })

# Initialize demo inventory
def initialize_inventory():
    """Initialize demo inventory with sample items"""
    
    # Create demo folders and items
    simulation_state["inventory"] = {
        "root": {
            "name": "My Inventory",
            "items": [
                {"id": 1, "name": "Box", "type": "object", "description": "A simple box"},
                {"id": 2, "name": "Sphere", "type": "object", "description": "A simple sphere"}
            ]
        },
        "clothing": {
            "name": "Clothing",
            "items": [
                {"id": 3, "name": "Blue Shirt", "type": "clothing", "description": "A blue shirt"},
                {"id": 4, "name": "Black Pants", "type": "clothing", "description": "Black pants"}
            ]
        },
        "objects": {
            "name": "Objects",
            "items": [
                {"id": 5, "name": "Chair", "type": "object", "description": "A wooden chair"},
                {"id": 6, "name": "Table", "type": "object", "description": "A wooden table"}
            ]
        },
        "textures": {
            "name": "Textures",
            "items": [
                {"id": 7, "name": "Wood", "type": "texture", "description": "Wood texture"},
                {"id": 8, "name": "Metal", "type": "texture", "description": "Metal texture"}
            ]
        }
    }
    
    logging.info("Demo inventory initialized with sample items")

# Chat message callback for demo
def on_chat_message(message):
    simulation_state["chat_messages"].append({
        "from": message["from"],
        "message": message["message"],
        "timestamp": time.time()
    })
    
    # Also send via websocket for real-time updates
    socketio.emit('chat_message', {
        "from": message["from"],
        "message": message["message"],
        "timestamp": time.time()
    })

# Teleport callback for demo
def on_teleport(region_name, x, y, z):
    simulation_state["current_region"] = region_name
    simulation_state["position"] = [x, y, z]
    
    # Also send via websocket for real-time updates
    socketio.emit('teleport', {
        "region": region_name,
        "position": [x, y, z],
        "timestamp": time.time()
    })

def run_simulation():
    """Run the KitelyView simulation"""
    # Set up logging
    logger = setup_logger()
    
    # Add custom handler for web interface
    web_handler = WebLogHandler()
    web_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    web_handler.setFormatter(formatter)
    logger.addHandler(web_handler)
    
    logger.info("Starting KitelyView Web Demo")
    
    # Initialize config
    config = Config()
    logger.info(f"Configuration loaded. Grid: {config.get('grid', 'name')}")
    
    # Update simulation status
    simulation_state["status"] = "initializing"
    socketio.emit('status_update', {"status": "initializing"})
    
    # Create grid connection
    connection = GridConnection(config)
    
    # Register callbacks
    connection.register_callback("chat_message", on_chat_message)
    connection.register_callback("teleport", on_teleport)
    
    # Simulate login
    logger.info("Simulating login to Kitely grid...")
    simulation_state["status"] = "logging_in"
    socketio.emit('status_update', {"status": "logging_in"})
    
    success, user_data = connection.login("Test", "User", "password123", "home")
    
    if success:
        logger.info(f"Login successful for user: {user_data['name']}")
        
        # Update simulation state
        simulation_state["logged_in"] = True
        simulation_state["user"] = {
            "name": user_data['name'],
            "id": user_data['id']
        }
        simulation_state["status"] = "logged_in"
        socketio.emit('status_update', {"status": "logged_in"})
        
        # Create user object
        user = User(user_data['id'], user_data['name'])
        logger.info(f"User object created: {user.get_full_name()}")
        
        # Simulate receiving a chat message from the system
        logger.info("Simulating received chat message...")
        simulation_state["status"] = "in_world"
        socketio.emit('status_update', {"status": "in_world"})
        
        chat_packet = "PACKET:ChatFromSimulator:Welcome to Kitely Plaza!"
        handler = connection.packet_handler if hasattr(connection, 'packet_handler') else None
        if handler:
            handler.handle_packet(chat_packet)
        else:
            # Direct callback since we're simulating
            on_chat_message({
                "from": "System",
                "message": "Welcome to Kitely Plaza!"
            })
            logger.info("CHAT: [System] Welcome to Kitely Plaza!")
        
        # Simulate teleport
        logger.info("Simulating teleport to Kitely Plaza...")
        connection.teleport("Kitely Plaza", 128, 128, 30)
        
        # Simulate sending a chat message
        logger.info("Simulating sending chat message...")
        connection.send_chat_message("Hello, Kitely World!")
        # Add to our own chat log
        on_chat_message({
            "from": "Test User",
            "message": "Hello, Kitely World!"
        })
        
        # Display user information
        logger.info("\nUser Information:")
        logger.info(f"Name: {user.get_full_name()}")
        logger.info(f"ID: {user.user_id}")
        logger.info(f"Current Region: {connection.current_region['name']}")
        logger.info(f"Position: {connection.current_region['position']}")
        
        # Show friends list
        if user.friends:
            logger.info("\nFriends:")
            for friend_id, friend_data in user.friends.items():
                status = "Online" if friend_data["online"] else "Offline"
                logger.info(f"- {friend_data['name']} ({status})")
        
        # Small delay to show how the application would run
        logger.info("\nRunning simulation for a few seconds...")
        for i in range(3):
            socketio.emit('status_update', {"status": f"running_simulation_{i+1}"})
            time.sleep(1)
            logger.info(f"Simulation running... ({i+1}/3)")
        
        # Simulate logout
        logger.info("\nLogging out...")
        simulation_state["status"] = "logging_out"
        socketio.emit('status_update', {"status": "logging_out"})
        
        connection.disconnect()
        
        # Update simulation state
        simulation_state["logged_in"] = False
        simulation_state["status"] = "completed"
        socketio.emit('status_update', {"status": "completed"})
    else:
        logger.error(f"Login failed: {user_data}")
        simulation_state["status"] = "error"
        socketio.emit('status_update', {"status": "error"})
    
    logger.info("KitelyView Web Demo completed")

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/events')
def get_events():
    """Get the latest events from the simulation"""
    events = []
    while not simulation_events.empty():
        events.append(simulation_events.get())
    return jsonify(events)

@app.route('/api/state')
def get_state():
    """Get the current simulation state"""
    return jsonify(simulation_state)

@app.route('/api/inventory')
def get_inventory():
    """Get user inventory"""
    return jsonify(simulation_state["inventory"])

@app.route('/api/appearance', methods=['GET', 'POST'])
def handle_appearance():
    """Get or update avatar appearance"""
    if request.method == 'GET':
        return jsonify(simulation_state["avatar_appearance"])
    
    # Handle POST - update appearance
    data = request.json
    if not data:
        return jsonify({"error": "No appearance data provided"}), 400
    
    # Update appearance data
    for key, value in data.items():
        if key in simulation_state["avatar_appearance"]:
            simulation_state["avatar_appearance"][key] = value
    
    logging.info(f"Avatar appearance updated: {data}")
    return jsonify({"status": "success", "appearance": simulation_state["avatar_appearance"]})

@app.route('/api/objects', methods=['GET', 'POST', 'DELETE'])
def handle_objects():
    """Get, create, or delete world objects"""
    if request.method == 'GET':
        return jsonify(simulation_state["objects"])
    
    if request.method == 'POST':
        # Create new object
        data = request.json
        if not data or "type" not in data:
            return jsonify({"error": "Invalid object data"}), 400
        
        # Generate object ID
        object_id = len(simulation_state["objects"]) + 1
        
        # Create new object
        new_object = {
            "id": object_id,
            "type": data["type"],
            "position": data.get("position", [0, 0, 0]),
            "rotation": data.get("rotation", [0, 0, 0]),
            "scale": data.get("scale", [1, 1, 1]),
            "color": data.get("color", "#f44336"),
            "properties": data.get("properties", {})
        }
        
        # Add to objects list
        simulation_state["objects"].append(new_object)
        
        logging.info(f"Object created: {new_object}")
        return jsonify({"status": "success", "object": new_object})
    
    if request.method == 'DELETE':
        # Delete object
        object_id = request.args.get('id')
        if not object_id:
            return jsonify({"error": "No object ID provided"}), 400
        
        # Find and remove object
        object_id = int(object_id)
        for i, obj in enumerate(simulation_state["objects"]):
            if obj["id"] == object_id:
                removed = simulation_state["objects"].pop(i)
                logging.info(f"Object deleted: {removed}")
                return jsonify({"status": "success", "id": object_id})
        
        return jsonify({"error": "Object not found"}), 404

@app.route('/api/start', methods=['POST'])
def start_simulation():
    """Start the simulation"""
    # Reset simulation state
    simulation_state["logged_in"] = False
    simulation_state["user"] = None
    simulation_state["current_region"] = None
    simulation_state["position"] = [0, 0, 0]
    simulation_state["chat_messages"] = []
    simulation_state["status"] = "starting"
    
    # Initialize inventory with sample items
    initialize_inventory()
    
    # Clear event queue
    while not simulation_events.empty():
        simulation_events.get()
    
    # Start simulation in a thread
    thread = threading.Thread(target=run_simulation)
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started"})

@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for manual login"""
    global simulation_state
    
    # Get login details from request
    data = request.json
    
    # Extract credentials
    first_name = data.get('first_name', 'Test')
    last_name = data.get('last_name', 'User')
    password = data.get('password', '')
    grid = data.get('grid', 'kitely')
    
    # Log login attempt with user info
    logging.info(f"API: Manual login to {grid.capitalize()} grid requested for user {first_name} {last_name}...")
    
    # Validate password (in a real system this would be a proper authentication)
    # For demo purposes, we'll accept any password with at least 4 characters
    if len(password) < 4:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 4 characters long'
        })
    
    # Add login event
    simulation_events.put({
        'type': 'login',
        'message': f'Login successful for {first_name} {last_name}',
        'timestamp': time.time(),
        'level': 'INFO'
    })
    
    # Create user ID from name
    user_id = f"user-{first_name.lower()}-{last_name.lower()}-{int(time.time())}"
    
    # Update simulation state to indicate login
    simulation_state["status"] = 'logged_in'
    simulation_state["logged_in"] = True
    simulation_state["user"] = {
        'id': user_id,
        'name': f"{first_name} {last_name}",
        'grid': grid.capitalize()
    }
    
    # Send status update via socket
    socketio.emit('status_update', {"status": "logged_in"})
    
    # Return success
    return jsonify({
        'success': True,
        'user': simulation_state["user"]
    })

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint for manual logout"""
    global simulation_state
    
    # In demo mode, simulate logout success
    logging.info("API: Manual logout from Kitely grid requested...")
    
    # Add logout event
    simulation_events.put({
        'type': 'logout',
        'message': 'Logged out',
        'timestamp': time.time(),
        'level': 'INFO'
    })
    
    # Update simulation state to indicate logout
    simulation_state["status"] = 'completed'
    simulation_state["logged_in"] = False
    simulation_state["user"] = None
    
    # Send status update via socket
    socketio.emit('status_update', {"status": "completed"})
    
    # Return success
    return jsonify({
        'success': True
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logging.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logging.info('Client disconnected')

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle chat message from client"""
    if not isinstance(data, dict) or 'message' not in data:
        return
    
    message = data["message"]
    
    # Add chat message to simulation state
    chat_data = {
        "from": "You",
        "message": message,
        "timestamp": time.time()
    }
    
    simulation_state["chat_messages"].append(chat_data)
    
    # Emit to all clients
    socketio.emit('chat_message', chat_data)
    
    # Log the message
    logging.info(f"Chat message from user: {message}")

@socketio.on('avatar_update')
def handle_avatar_update(data):
    """Handle avatar appearance update from client"""
    if not isinstance(data, dict):
        return
    
    # Update avatar appearance
    for key, value in data.items():
        if key in simulation_state["avatar_appearance"]:
            simulation_state["avatar_appearance"][key] = value
    
    # Log the update
    logging.info(f"Avatar appearance updated via socket: {data}")
    
    # Emit update to all clients
    socketio.emit('avatar_updated', simulation_state["avatar_appearance"])

@socketio.on('object_create')
def handle_object_create(data):
    """Handle object creation from client"""
    if not isinstance(data, dict) or 'type' not in data:
        return
    
    # Generate object ID
    object_id = len(simulation_state["objects"]) + 1
    
    # Create new object
    new_object = {
        "id": object_id,
        "type": data["type"],
        "position": data.get("position", [0, 0, 0]),
        "rotation": data.get("rotation", [0, 0, 0]),
        "scale": data.get("scale", [1, 1, 1]),
        "color": data.get("color", "#f44336"),
        "properties": data.get("properties", {})
    }
    
    # Add to objects list
    simulation_state["objects"].append(new_object)
    
    # Log the creation
    logging.info(f"Object created via socket: {new_object}")
    
    # Emit update to all clients
    socketio.emit('object_created', new_object)

def create_default_directories():
    """Create necessary directories"""
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/js/three', exist_ok=True)
    os.makedirs('static/js/ui', exist_ok=True)
    os.makedirs('static/img', exist_ok=True)
    os.makedirs('static/models', exist_ok=True)
    os.makedirs('static/textures', exist_ok=True)

if __name__ == '__main__':
    create_default_directories()
    # Use Replit-friendly settings
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True, log_output=True)