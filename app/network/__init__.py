"""
Network package for the KitelyView application.
Handles all communication with OpenSimulator grids.
"""

from app.network.connection import GridConnection
from app.network.opensim_protocol import OpenSimProtocol
from app.network.packet_handler import PacketHandler
