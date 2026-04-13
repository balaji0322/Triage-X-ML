# backend/app/location_tracking.py
"""
Real-Time GPS Location Tracking System
Handles ambulance location updates and broadcasting
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from loguru import logger as log
from datetime import datetime
import math
import json

from .auth import require_ambulance, require_hospital, get_current_user
from .database import get_db

router = APIRouter()


# ============ SCHEMAS ============

class LocationUpdate(BaseModel):
    """Ambulance location update."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed: Optional[float] = Field(default=0, ge=0)  # km/h
    heading: Optional[float] = Field(default=0, ge=0, le=360)  # degrees


class HospitalInfo(BaseModel):
    """Hospital information with location."""
    hospital_id: str
    hospital_name: str
    address: str
    latitude: float
    longitude: float
    available_beds: int
    current_load: int
    distance_km: float
    score: float


class NearestHospitalsResponse(BaseModel):
    """Response with nearest hospitals."""
    ambulance_location: Dict[str, float]
    hospitals: List[HospitalInfo]
    recommended_hospital: HospitalInfo


# ============ WEBSOCKET CONNECTION MANAGER ============

class LocationWebSocketManager:
    """Manages WebSocket connections for real-time location tracking."""
    
    def __init__(self):
        # Store connections by role
        self.ambulance_connections: Dict[str, WebSocket] = {}  # ambulance_id -> websocket
        self.hospital_connections: List[WebSocket] = []
        
    async def connect_ambulance(self, websocket: WebSocket, ambulance_id: str):
        """Connect ambulance for location updates."""
        await websocket.accept()
        self.ambulance_connections[ambulance_id] = websocket
        log.info(f"📍 Ambulance {ambulance_id} connected for location tracking")
        
    async def connect_hospital(self, websocket: WebSocket):
        """Connect hospital for receiving location updates."""
        await websocket.accept()
        self.hospital_connections.append(websocket)
        log.info(f"🏥 Hospital connected for location tracking ({len(self.hospital_connections)} total)")
        
    def disconnect_ambulance(self, ambulance_id: str):
        """Disconnect ambulance."""
        if ambulance_id in self.ambulance_connections:
            del self.ambulance_connections[ambulance_id]
            log.info(f"📍 Ambulance {ambulance_id} disconnected")
            
    def disconnect_hospital(self, websocket: WebSocket):
        """Disconnect hospital."""
        if websocket in self.hospital_connections:
            self.hospital_connections.remove(websocket)
            log.info(f"🏥 Hospital disconnected ({len(self.hospital_connections)} remaining)")
            
    async def broadcast_location(self, ambulance_id: str, location_data: dict):
        """Broadcast ambulance location to all connected hospitals."""
        message = {
            "type": "location_update",
            "ambulance_id": ambulance_id,
            "location": location_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all hospitals
        disconnected = []
        for websocket in self.hospital_connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                log.error(f"Failed to send location to hospital: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected hospitals
        for ws in disconnected:
            self.disconnect_hospital(ws)
            
        log.debug(f"📡 Location broadcasted to {len(self.hospital_connections)} hospitals")


# Global location manager
location_manager = LocationWebSocketManager()


# ============ DISTANCE CALCULATION ============

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


def calculate_hospital_score(distance_km: float, available_beds: int, current_load: int) -> float:
    """
    Calculate hospital recommendation score.
    Lower score = better choice
    
    Formula: score = (0.5 * distance) + (-0.3 * beds) + (0.2 * load)
    """
    score = (0.5 * distance_km) + (-0.3 * available_beds) + (0.2 * current_load)
    return round(score, 2)


# ============ WEBSOCKET ENDPOINTS ============

@router.websocket("/ws/location")
async def location_tracking_websocket(
    websocket: WebSocket,
    role: str = Query(..., regex="^(ambulance|hospital)$"),
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time location tracking.
    
    - Ambulances: Send location updates every 3-5 seconds
    - Hospitals: Receive real-time ambulance locations
    """
    
    # For ambulances, we need authentication
    if role == "ambulance":
        if not token:
            await websocket.close(code=1008, reason="Authentication required")
            return
            
        try:
            # Verify token and get ambulance ID
            from .auth import decode_token
            payload = decode_token(token)
            ambulance_id = payload.get("sub")
            
            if not ambulance_id or payload.get("role") != "ambulance":
                await websocket.close(code=1008, reason="Invalid ambulance token")
                return
                
            await location_manager.connect_ambulance(websocket, ambulance_id)
            
            try:
                # Send connection confirmation
                await websocket.send_json({
                    "type": "connection",
                    "status": "connected",
                    "role": "ambulance",
                    "ambulance_id": ambulance_id
                })
                
                # Receive location updates
                while True:
                    data = await websocket.receive_text()
                    
                    try:
                        location_data = json.loads(data)
                        
                        # Validate location data
                        if "latitude" in location_data and "longitude" in location_data:
                            # Store in database
                            db = get_db()
                            db.ambulance_locations.update_one(
                                {"ambulance_id": ambulance_id},
                                {
                                    "$set": {
                                        "latitude": location_data["latitude"],
                                        "longitude": location_data["longitude"],
                                        "speed": location_data.get("speed", 0),
                                        "heading": location_data.get("heading", 0),
                                        "timestamp": datetime.utcnow()
                                    }
                                },
                                upsert=True
                            )
                            
                            # Broadcast to hospitals
                            await location_manager.broadcast_location(ambulance_id, location_data)
                            
                            # Send acknowledgment
                            await websocket.send_json({
                                "type": "ack",
                                "status": "received"
                            })
                            
                    except json.JSONDecodeError:
                        log.error(f"Invalid JSON from ambulance {ambulance_id}")
                        
            except WebSocketDisconnect:
                location_manager.disconnect_ambulance(ambulance_id)
                
        except Exception as e:
            log.error(f"Ambulance WebSocket error: {e}")
            await websocket.close(code=1011, reason="Internal error")
            
    elif role == "hospital":
        await location_manager.connect_hospital(websocket)
        
        try:
            # Send connection confirmation
            await websocket.send_json({
                "type": "connection",
                "status": "connected",
                "role": "hospital"
            })
            
            # Keep connection alive
            while True:
                data = await websocket.receive_text()
                
                # Handle ping/pong
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
                    
        except WebSocketDisconnect:
            location_manager.disconnect_hospital(websocket)


# ============ REST API ENDPOINTS ============

@router.get("/nearest-hospitals", response_model=NearestHospitalsResponse)
async def get_nearest_hospitals(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    limit: int = Query(default=10, ge=1, le=50),
    current_user: dict = Depends(require_ambulance)
):
    """
    Get nearest hospitals with AI-based recommendation.
    
    Returns hospitals sorted by score (distance, beds, load).
    """
    db = get_db()
    
    try:
        # Get all hospitals with location data
        hospitals = list(db.hospitals.find({
            "latitude": {"$exists": True},
            "longitude": {"$exists": True}
        }))
        
        if not hospitals:
            raise HTTPException(status_code=404, detail="No hospitals with location data found")
        
        # Calculate distance and score for each hospital
        hospital_scores = []
        
        for hospital in hospitals:
            # Calculate distance
            distance = haversine_distance(
                lat, lng,
                hospital["latitude"],
                hospital["longitude"]
            )
            
            # Get hospital data
            available_beds = hospital.get("available_beds", 10)
            current_load = hospital.get("current_load", 0)
            
            # Calculate score
            score = calculate_hospital_score(distance, available_beds, current_load)
            
            hospital_info = HospitalInfo(
                hospital_id=hospital["hospital_id"],
                hospital_name=hospital["hospital_name"],
                address=hospital["address"],
                latitude=hospital["latitude"],
                longitude=hospital["longitude"],
                available_beds=available_beds,
                current_load=current_load,
                distance_km=distance,
                score=score
            )
            
            hospital_scores.append(hospital_info)
        
        # Sort by score (lower is better)
        hospital_scores.sort(key=lambda x: x.score)
        
        # Limit results
        nearest_hospitals = hospital_scores[:limit]
        
        # Recommended hospital is the one with lowest score
        recommended = nearest_hospitals[0] if nearest_hospitals else None
        
        log.info(f"✅ Found {len(nearest_hospitals)} nearest hospitals. Recommended: {recommended.hospital_id if recommended else 'None'}")
        
        return NearestHospitalsResponse(
            ambulance_location={"latitude": lat, "longitude": lng},
            hospitals=nearest_hospitals,
            recommended_hospital=recommended
        )
        
    except Exception as e:
        log.error(f"❌ Failed to get nearest hospitals: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/ambulance-locations")
async def get_all_ambulance_locations(
    current_user: dict = Depends(require_hospital)
):
    """
    Get current locations of all active ambulances.
    For hospital dashboard map initialization.
    """
    db = get_db()
    
    try:
        # Get recent locations (last 5 minutes)
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        
        locations = list(db.ambulance_locations.find({
            "timestamp": {"$gte": cutoff_time}
        }))
        
        # Format response
        result = []
        for loc in locations:
            # Get ambulance details
            ambulance = db.ambulances.find_one({"_id": loc["ambulance_id"]})
            
            if ambulance:
                result.append({
                    "ambulance_id": loc["ambulance_id"],
                    "ambulance_number": ambulance.get("ambulance_number", "Unknown"),
                    "driver_name": ambulance.get("driver_name", "Unknown"),
                    "latitude": loc["latitude"],
                    "longitude": loc["longitude"],
                    "speed": loc.get("speed", 0),
                    "heading": loc.get("heading", 0),
                    "timestamp": loc["timestamp"].isoformat()
                })
        
        log.info(f"✅ Retrieved {len(result)} active ambulance locations")
        return result
        
    except Exception as e:
        log.error(f"❌ Failed to get ambulance locations: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/update-hospital-data")
async def update_hospital_data(
    hospital_id: str,
    available_beds: int = Query(..., ge=0),
    current_load: int = Query(..., ge=0),
    current_user: dict = Depends(require_hospital)
):
    """
    Update hospital bed availability and current load.
    For real-time hospital capacity management.
    """
    db = get_db()
    
    try:
        result = db.hospitals.update_one(
            {"hospital_id": hospital_id},
            {
                "$set": {
                    "available_beds": available_beds,
                    "current_load": current_load,
                    "last_updated": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        log.info(f"✅ Updated hospital {hospital_id}: beds={available_beds}, load={current_load}")
        
        return {
            "status": "success",
            "hospital_id": hospital_id,
            "available_beds": available_beds,
            "current_load": current_load
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Failed to update hospital data: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
