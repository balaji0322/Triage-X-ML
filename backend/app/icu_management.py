# backend/app/icu_management.py
"""
ICU Bed Management System
Real-time ICU bed availability tracking and allocation
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional
from loguru import logger as log
from datetime import datetime

from .auth import require_hospital, get_current_user
from .database import get_db
from .websocket_manager import manager

router = APIRouter()


# ============ SCHEMAS ============

class ICUUpdateRequest(BaseModel):
    """Request to update ICU bed availability."""
    hospital_id: str
    icu_total: int = Field(..., ge=0, description="Total ICU beds")
    icu_available: int = Field(..., ge=0, description="Available ICU beds")
    
    @validator('icu_available')
    def validate_available(cls, v, values):
        """Ensure available beds don't exceed total beds."""
        if 'icu_total' in values and v > values['icu_total']:
            raise ValueError('Available beds cannot exceed total beds')
        return v


class ICUStatusResponse(BaseModel):
    """Response with ICU status."""
    hospital_id: str
    hospital_name: str
    icu_total: int
    icu_available: int
    icu_occupied: int
    occupancy_rate: float
    current_load: int
    last_updated: str


class HospitalICUStats(BaseModel):
    """Hospital ICU statistics."""
    total_hospitals: int
    total_icu_beds: int
    total_available: int
    total_occupied: int
    average_occupancy: float
    hospitals_at_capacity: int


# ============ ICU MANAGEMENT ENDPOINTS ============

@router.put("/hospital/update-icu", response_model=ICUStatusResponse)
async def update_icu_beds(
    request: ICUUpdateRequest,
    current_user: dict = Depends(require_hospital)
):
    """
    Update ICU bed availability for a hospital.
    
    - Validates bed counts
    - Updates MongoDB
    - Calculates current load
    - Broadcasts update via WebSocket
    """
    db = get_db()
    
    try:
        # Verify hospital exists
        hospital = db.hospitals.find_one({"hospital_id": request.hospital_id})
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        # Verify user has permission (can only update own hospital)
        if current_user["payload"].get("hospital_id") != request.hospital_id:
            raise HTTPException(
                status_code=403, 
                detail="You can only update your own hospital's ICU beds"
            )
        
        # Calculate metrics
        icu_occupied = request.icu_total - request.icu_available
        occupancy_rate = (icu_occupied / request.icu_total * 100) if request.icu_total > 0 else 0
        current_load = icu_occupied
        
        # Update database
        update_data = {
            "icu_total": request.icu_total,
            "icu_available": request.icu_available,
            "icu_occupied": icu_occupied,
            "occupancy_rate": round(occupancy_rate, 2),
            "current_load": current_load,
            "last_updated": datetime.utcnow()
        }
        
        result = db.hospitals.update_one(
            {"hospital_id": request.hospital_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            log.warning(f"No changes made to hospital {request.hospital_id}")
        
        log.info(f"✅ ICU beds updated for {request.hospital_id}: {request.icu_available}/{request.icu_total} available")
        
        # Prepare response
        response = ICUStatusResponse(
            hospital_id=request.hospital_id,
            hospital_name=hospital["hospital_name"],
            icu_total=request.icu_total,
            icu_available=request.icu_available,
            icu_occupied=icu_occupied,
            occupancy_rate=round(occupancy_rate, 2),
            current_load=current_load,
            last_updated=datetime.utcnow().isoformat()
        )
        
        # 📡 Broadcast ICU update to all connected clients via WebSocket
        try:
            await manager.broadcast_to_all({
                "type": "icu_update",
                "hospital_id": request.hospital_id,
                "hospital_name": hospital["hospital_name"],
                "icu_total": request.icu_total,
                "icu_available": request.icu_available,
                "icu_occupied": icu_occupied,
                "occupancy_rate": round(occupancy_rate, 2),
                "timestamp": datetime.utcnow().isoformat()
            })
            log.info(f"📡 ICU update broadcasted to all clients")
        except Exception as e:
            log.warning(f"⚠️ WebSocket broadcast failed (non-critical): {e}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Failed to update ICU beds: {e}")
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")


@router.get("/hospital/icu-status/{hospital_id}", response_model=ICUStatusResponse)
async def get_icu_status(
    hospital_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get current ICU status for a specific hospital.
    """
    db = get_db()
    
    try:
        hospital = db.hospitals.find_one({"hospital_id": hospital_id})
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        response = ICUStatusResponse(
            hospital_id=hospital["hospital_id"],
            hospital_name=hospital["hospital_name"],
            icu_total=hospital.get("icu_total", 0),
            icu_available=hospital.get("icu_available", 0),
            icu_occupied=hospital.get("icu_occupied", 0),
            occupancy_rate=hospital.get("occupancy_rate", 0),
            current_load=hospital.get("current_load", 0),
            last_updated=hospital.get("last_updated", datetime.utcnow()).isoformat()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Failed to get ICU status: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/hospital/icu-stats", response_model=HospitalICUStats)
async def get_icu_statistics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get overall ICU statistics across all hospitals.
    """
    db = get_db()
    
    try:
        # Aggregate ICU statistics
        pipeline = [
            {
                "$match": {
                    "icu_total": {"$exists": True}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_hospitals": {"$sum": 1},
                    "total_icu_beds": {"$sum": "$icu_total"},
                    "total_available": {"$sum": "$icu_available"},
                    "total_occupied": {"$sum": "$icu_occupied"},
                    "hospitals_at_capacity": {
                        "$sum": {
                            "$cond": [{"$eq": ["$icu_available", 0]}, 1, 0]
                        }
                    }
                }
            }
        ]
        
        result = list(db.hospitals.aggregate(pipeline))
        
        if not result:
            return HospitalICUStats(
                total_hospitals=0,
                total_icu_beds=0,
                total_available=0,
                total_occupied=0,
                average_occupancy=0,
                hospitals_at_capacity=0
            )
        
        stats = result[0]
        total_beds = stats["total_icu_beds"]
        total_occupied = stats["total_occupied"]
        average_occupancy = (total_occupied / total_beds * 100) if total_beds > 0 else 0
        
        response = HospitalICUStats(
            total_hospitals=stats["total_hospitals"],
            total_icu_beds=total_beds,
            total_available=stats["total_available"],
            total_occupied=total_occupied,
            average_occupancy=round(average_occupancy, 2),
            hospitals_at_capacity=stats["hospitals_at_capacity"]
        )
        
        log.info(f"✅ ICU statistics: {response.total_available}/{response.total_icu_beds} available")
        
        return response
        
    except Exception as e:
        log.error(f"❌ Failed to get ICU statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/hospitals/with-icu")
async def get_hospitals_with_icu(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all hospitals with ICU bed information.
    Used for ambulance dashboard to show ICU availability.
    """
    db = get_db()
    
    try:
        hospitals = list(db.hospitals.find({
            "icu_total": {"$exists": True},
            "latitude": {"$exists": True},
            "longitude": {"$exists": True}
        }))
        
        result = []
        for hospital in hospitals:
            result.append({
                "hospital_id": hospital["hospital_id"],
                "hospital_name": hospital["hospital_name"],
                "address": hospital["address"],
                "latitude": hospital["latitude"],
                "longitude": hospital["longitude"],
                "icu_total": hospital.get("icu_total", 0),
                "icu_available": hospital.get("icu_available", 0),
                "icu_occupied": hospital.get("icu_occupied", 0),
                "occupancy_rate": hospital.get("occupancy_rate", 0),
                "available_beds": hospital.get("available_beds", 0),
                "current_load": hospital.get("current_load", 0)
            })
        
        log.info(f"✅ Retrieved {len(result)} hospitals with ICU data")
        return result
        
    except Exception as e:
        log.error(f"❌ Failed to get hospitals with ICU: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
