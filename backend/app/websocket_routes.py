# backend/app/websocket_routes.py
"""
WebSocket Routes for Real-Time Communication
Provides WebSocket endpoints for live case updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from loguru import logger as log
from datetime import datetime
from .websocket_manager import manager
import json

router = APIRouter()


@router.websocket("/ws/cases")
async def websocket_cases_endpoint(
    websocket: WebSocket,
    role: str = Query(default="hospital", regex="^(hospital|ambulance)$")
):
    """
    WebSocket endpoint for real-time case updates.
    
    Query Parameters:
    - role: "hospital" or "ambulance" (default: "hospital")
    
    Usage:
    - Hospitals connect to receive live case updates
    - Ambulances can connect to receive acknowledgments
    """
    await manager.connect(websocket, role)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "role": role,
            "message": f"Connected as {role}",
            "active_connections": manager.get_connection_count(role)
        }, websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            # Receive messages from client (for heartbeat or commands)
            data = await websocket.receive_text()
            
            # Handle ping/pong for connection health
            if data == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": str(datetime.utcnow())
                }, websocket)
            else:
                # Echo back for debugging
                log.debug(f"📨 Received from {role}: {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, role)
        log.info(f"🔌 {role} disconnected")
    except Exception as e:
        log.error(f"❌ WebSocket error for {role}: {e}")
        manager.disconnect(websocket, role)


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status."""
    return {
        "hospital_connections": manager.get_connection_count("hospital"),
        "ambulance_connections": manager.get_connection_count("ambulance"),
        "total_connections": (
            manager.get_connection_count("hospital") + 
            manager.get_connection_count("ambulance")
        )
    }
