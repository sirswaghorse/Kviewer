#!/usr/bin/env python3
"""
KitelyView Demo - A simplified demonstration of the KitelyView application.
This script demonstrates the key functionality without requiring a GUI.
"""

import sys
import os
import logging
import time
from app.utils.logger import setup_logger
from app.config import Config
from app.models.user import User
from app.network.connection import GridConnection

# Chat message callback for demo
def on_chat_message(message):
    logger = logging.getLogger("kitelyview")
    logger.info(f"CHAT: [{message['from']}] {message['message']}")

# Teleport callback for demo
def on_teleport(region_name, x, y, z):
    logger = logging.getLogger("kitelyview")
    logger.info(f"TELEPORT: Arrived at {region_name} ({x}, {y}, {z})")

def main():
    """Main entry point for the demo application"""
    # Set up logging
    logger = setup_logger()
    logger.info("Starting KitelyView Demo")
    
    # Initialize config
    config = Config()
    logger.info(f"Configuration loaded. Grid: {config.get('grid', 'name')}")
    
    # Create grid connection
    connection = GridConnection(config)
    
    # Register callbacks
    connection.register_callback("chat_message", on_chat_message)
    connection.register_callback("teleport", on_teleport)
    
    # Simulate login
    logger.info("Simulating login to Kitely grid...")
    success, user_data = connection.login("Test", "User", "password123", "home")
    
    if success:
        logger.info(f"Login successful for user: {user_data['name']}")
        
        # Create user object
        user = User(user_data['id'], user_data['name'])
        logger.info(f"User object created: {user.get_full_name()}")
        
        # Simulate receiving a chat message from the system
        # This would normally come from the network layer
        logger.info("Simulating received chat message...")
        chat_packet = "PACKET:ChatFromSimulator:Welcome to Kitely Plaza!"
        handler = connection.packet_handler if hasattr(connection, 'packet_handler') else None
        if handler:
            handler.handle_packet(chat_packet)
        else:
            logger.info("SIMULATED: [System] Welcome to Kitely Plaza!")
        
        # Simulate teleport
        logger.info("Simulating teleport to Kitely Plaza...")
        connection.teleport("Kitely Plaza", 128, 128, 30)
        
        # Simulate sending a chat message
        logger.info("Simulating sending chat message...")
        connection.send_chat_message("Hello, Kitely World!")
        
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
            time.sleep(1)
            logger.info(f"Simulation running... ({i+1}/3)")
        
        # Simulate logout
        logger.info("\nLogging out...")
        connection.disconnect()
    else:
        logger.error(f"Login failed: {user_data}")
    
    logger.info("KitelyView Demo completed")

if __name__ == "__main__":
    main()