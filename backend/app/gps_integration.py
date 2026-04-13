# backend/app/gps_integration.py
"""
GPS Integration Module for Real-Time Location Tracking
Provides distance calculation, ETA estimation, and hospital routing
"""
from typing import Dict, List, Tuple, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger as log
import math
from datetime import datetime, timedelta

from .auth import require_ambulance
from .database import get_db

router = APIRouter()


# ============ SCHEMAS ============

class GPSCoordinates(BaseModel):
    """GPS coordinates."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class RouteRequest(BaseModel):
    """Request for route calculation."""
    ambulance_location: GPSCoordinates
    hospital_id: str


class RouteResponse(BaseModel):
    """Response with route information."""
    hospital_id: str
    hospital_name: str
    hospital_location: GPSCoordinates
    distance_km: float
    estimated_time_minutes: int
    route_description: str


class NearestHospitalsRequest(BaseModel):
    """Request for nearest hospitals."""
    ambulance_location: GPSCoordinates
    severity: str
    limit: int = Field(default=5, ge=1, le=10)


class NearestHospitalsResponse(BaseModel):
    """Response with nearest hospitals."""
    hospitals: List[Dict]
    ambulance_location: GPSCoordinates


# ============ HOSPITAL COORDINATES DATABASE ============
# In production, these would be stored in MongoDB with actual GPS coordinates

HOSPITAL_COORDINATES = {
    # Chennai hospitals
    "HOSP-CHE": (13.0827, 80.2707),
    "HOSP-CHE-1001": (13.0878, 80.2785),
    "HOSP-CHE-1002": (13.0679, 80.2495),
    "HOSP-CHE-1003": (13.1067, 80.2897),
    
    # Bangalore hospitals
    "HOSP-BAN": (12.9716, 77.5946),
    "HOSP-BAN-2001": (12.9698, 77.6489),
    "HOSP-BAN-2002": (12.9352, 77.6245),
    
    # Mumbai hospitals
    "HOSP-MUM": (19.0760, 72.8777),
    "HOSP-MUM-3001": (19.1136, 72.8697),
    "HOSP-MUM-3002": (19.0176, 72.8562),
    
    # Delhi hospitals
    "HOSP-DEL": (28.7041, 77.1025),
    "HOSP-DEL-4001": (28.6139, 77.2090),
    "HOSP-DEL-4002": (28.5355, 77.3910),
}


# ============ DISTANCE & ETA CALCULATIONS ============

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


def calculate_eta(distance_km: float, severity: str = "Moderate") -> int:
    """
    Calculate estimated time of arrival in minutes.
    
    Assumptions:
    - Urgent cases: 80 km/h average (emergency speed)
    - Moderate cases: 60 km/h average
    - Minor cases: 50 km/h average
    """
    speed_map = {
        "Urgent": 80,
        "Immediate": 80,
        "Moderate": 60,
        "Minor": 50
    }
    
    avg_speed = speed_map.get(severity, 60)
    time_hours = distance_km / avg_speed
    time_minutes = int(time_hours * 60)
    
    return max(time_minutes, 1)  # Minimum 1 minute


def get_hospital_coordinates(hospital_id: str) -> Optional[Tuple[float, float]]:
    """Get hospital GPS coordinates from database or default mapping."""
    # Check if exact match exists
    if hospital_id in HOSPITAL_COORDINATES:
        return HOSPITAL_COORDINATES[hospital_id]
    
    # Try prefix match (e.g., HOSP-CHE-1234 -> HOSP-CHE)
    for prefix in ["HOSP-CHE", "HOSP-BAN", "HOSP-MUM", "HOSP-DEL"]:
        if hospital_id.startswith(prefix):
            return HOSPITAL_COORDINATES.get(prefix, (13.0827, 80.2707))
    
    # Default to Chennai
    return (13.0827, 80.2707)


# ============ API ENDPOINTS ============

@router.post("/gps/route", response_model=RouteResponse)
async def calculate_route(
    request: RouteRequest,
    current_user: dict = Depends(require_ambulance)
):
    """
    📍 Calculate route from ambulance to hospital.
    
    Returns:
    - Distance in kilometers
    - Estimated time of arrival
    - Route description
    """
    db = get_db()
    
    try:
        # Get hospital details
        hospital = db.hospitals.find_one({"hospital_id": request.hospital_id})
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        # Get hospital coordinates
        hospital_coords = get_hospital_coordinates(request.hospital_id)
        
        # Calculate distance
        distance = haversine_distance(
            request.ambulance_location.latitude,
            request.ambulance_location.longitude,
            hospital_coords[0],
            hospital_coords[1]
        )
        
        # Calculate ETA (assume Moderate severity if not specified)
        eta = calculate_eta(distance, "Moderate")
        
        # Generate route description
        direction = get_direction(
            request.ambulance_location.latitude,
            request.ambulance_location.longitude,
            hospital_coords[0],
            hospital_coords[1]
        )
        
        route_description = (
            f"Head {direction} for {distance} km. "
            f"Estimated arrival: {eta} minutes. "
            f"Destination: {hospital['hospital_name']}"
        )
        
        log.info(f"✅ Route calculated: {distance} km, ETA {eta} min")
        
        return RouteResponse(
            hospital_id=request.hospital_id,
            hospital_name=hospital["hospital_name"],
            hospital_location=GPSCoordinates(
                latitude=hospital_coords[0],
                longitude=hospital_coords[1]
            ),
            distance_km=distance,
            estimated_time_minutes=eta,
            route_description=route_description
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Route calculation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Route calculation error: {str(e)}")


@router.post("/gps/nearest-hospitals", response_model=NearestHospitalsResponse)
async def find_nearest_hospitals(
    request: NearestHospitalsRequest,
    current_user: dict = Depends(require_ambulance)
):
    """
    📍 Find nearest hospitals based on ambulance location.
    
    Returns list of hospitals sorted by distance with ETA.
    """
    db = get_db()
    
    try:
        # Get all hospitals
        hospitals = list(db.hospitals.find())
        
        if not hospitals:
            raise HTTPException(status_code=404, detail="No hospitals found")
        
        # Calculate distance to each hospital
        hospital_distances = []
        
        for hospital in hospitals:
            hospital_id = hospital["hospital_id"]
            hospital_coords = get_hospital_coordinates(hospital_id)
            
            distance = haversine_distance(
                request.ambulance_location.latitude,
                request.ambulance_location.longitude,
                hospital_coords[0],
                hospital_coords[1]
            )
            
            eta = calculate_eta(distance, request.severity)
            
            # Get current load
            load = db.cases.count_documents({
                "hospital_assigned": hospital_id,
                "status": "pending"
            })
            
            hospital_distances.append({
                "hospital_id": hospital_id,
                "hospital_name": hospital["hospital_name"],
                "address": hospital["address"],
                "distance_km": distance,
                "eta_minutes": eta,
                "current_load": load,
                "coordinates": {
                    "latitude": hospital_coords[0],
                    "longitude": hospital_coords[1]
                }
            })
        
        # Sort by distance
        hospital_distances.sort(key=lambda x: x["distance_km"])
        
        # Limit results
        nearest = hospital_distances[:request.limit]
        
        log.info(f"✅ Found {len(nearest)} nearest hospitals")
        
        return NearestHospitalsResponse(
            hospitals=nearest,
            ambulance_location=request.ambulance_location
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Nearest hospitals search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.post("/gps/update-location")
async def update_ambulance_location(
    location: GPSCoordinates,
    current_user: dict = Depends(require_ambulance)
):
    """
    📍 Update ambulance real-time location.
    
    Stores location in database for tracking and analytics.
    """
    db = get_db()
    
    try:
        ambulance_id = current_user["user_id"]
        
        # Update or create location record
        db.ambulance_locations.update_one(
            {"ambulance_id": ambulance_id},
            {
                "$set": {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "timestamp": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        log.info(f"✅ Location updated for ambulance {ambulance_id}")
        
        return {
            "status": "success",
            "message": "Location updated",
            "location": {
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        }
        
    except Exception as e:
        log.error(f"❌ Location update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Location update error: {str(e)}")


# ============ HELPER FUNCTIONS ============

def get_direction(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
    """Get cardinal direction from point 1 to point 2."""
    delta_lon = lon2 - lon1
    delta_lat = lat2 - lat1
    
    # Calculate bearing
    bearing = math.atan2(delta_lon, delta_lat)
    bearing_degrees = math.degrees(bearing)
    
    # Normalize to 0-360
    bearing_degrees = (bearing_degrees + 360) % 360
    
    # Convert to cardinal direction
    directions = [
        "North", "Northeast", "East", "Southeast",
        "South", "Southwest", "West", "Northwest"
    ]
    
    index = int((bearing_degrees + 22.5) / 45) % 8
    return directions[index]
