# backend/app/websocket_manager.py
"""
WebSocket Connection Manager for Real-Time Case Broadcasting
Manages active WebSocket connections and broadcasts case updates to hospitals
"""
from fastapi import WebSocket
from typing import List, Dict
from loguru import logger as log
import json
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Store active connections by role
        self.active_connections: Dict[str, List[WebSocket]] = {
            "hospital": [],
            "ambulance": []
        }
    
    async def connect(self, websocket: WebSocket, role: str = "hospital"):
        """Accept and store a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[role].append(websocket)
        log.info(f"✅ WebSocket connected: {role} (Total: {len(self.active_connections[role])})")
    
    def disconnect(self, websocket: WebSocket, role: str = "hospital"):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections[role]:
            self.active_connections[role].remove(websocket)
            log.info(f"🔌 WebSocket disconnected: {role} (Remaining: {len(self.active_connections[role])})")
    
    async def broadcast_to_hospitals(self, message: dict):
        """Broadcast a message to all connected hospital clients."""
        disconnected = []
        
        for connection in self.active_connections["hospital"]:
            try:
                await connection.send_json(message)
                log.debug(f"📤 Broadcasted to hospital client")
            except Exception as e:
                log.error(f"❌ Failed to send to hospital: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn, "hospital")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            log.error(f"❌ Failed to send personal message: {e}")
    
    def get_connection_count(self, role: str = "hospital") -> int:
        """Get the number of active connections for a role."""
        return len(self.active_connections[role])


# Global connection manager instance
manager = ConnectionManager()
