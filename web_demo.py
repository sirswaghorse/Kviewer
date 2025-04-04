#!/usr/bin/env python3
"""
KitelyView Web Demo - A web-based demonstration of the KitelyView application.
This script provides a web interface to visualize the simulation.
"""

import sys
import os
import logging
import time
import json
import threading
import queue
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO

from app.utils.logger import setup_logger
from app.config import Config
from app.models.user import User
from app.network.connection import GridConnection

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kitelyview-demo-secret'
socketio = SocketIO(app)

# Global variables for simulation state
simulation_events = queue.Queue()
simulation_state = {
    "logged_in": False,
    "user": None,
    "current_region": None,
    "position": [0, 0, 0],
    "chat_messages": [],
    "inventory": [],
    "status": "idle"
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

@app.route('/api/start', methods=['POST'])
def start_simulation():
    """Start the simulation"""
    # Reset simulation state
    simulation_state["logged_in"] = False
    simulation_state["user"] = None
    simulation_state["current_region"] = None
    simulation_state["position"] = [0, 0, 0]
    simulation_state["chat_messages"] = []
    simulation_state["inventory"] = []
    simulation_state["status"] = "starting"
    
    # Clear event queue
    while not simulation_events.empty():
        simulation_events.get()
    
    # Start simulation in a thread
    thread = threading.Thread(target=run_simulation)
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started"})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

def create_default_directories():
    """Create necessary directories"""
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/img', exist_ok=True)

if __name__ == '__main__':
    create_default_directories()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)