# backend/app/auth_routes.py
from fastapi import APIRouter, HTTPException, status, Depends
from loguru import logger as log
from datetime import datetime
import uuid
import re

from .auth_schemas import (
    AmbulanceSignup, AmbulanceLogin, AmbulanceResponse,
    HospitalSignup, HospitalLogin, HospitalResponse,
    TokenResponse, CaseCreate, CaseResponse
)
from .auth import hash_password, verify_password, create_access_token, require_ambulance, require_hospital
from .database import get_db

router = APIRouter()


def generate_hospital_id(address: str) -> str:
    """Generate hospital ID in format HOSP-{CITYCODE}-{4DIGIT}"""
    # Extract city code from address (first 3 letters of first word, uppercase)
    words = re.findall(r'\b\w+\b', address)
    city_code = words[0][:3].upper() if words else "CTY"
    
    # Generate 4-digit random number
    random_digits = str(uuid.uuid4().int)[:4]
    
    return f"HOSP-{city_code}-{random_digits}"


# ============ AMBULANCE ROUTES ============
@router.post("/ambulance/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def ambulance_signup(data: AmbulanceSignup):
    """Register a new ambulance."""
    db = get_db()
    
    # Check if ambulance number already exists
    existing = db.ambulances.find_one({"ambulance_number": data.ambulance_number})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ambulance number already registered"
        )
    
    # Create ambulance record
    ambulance_id = str(uuid.uuid4())
    ambulance_doc = {
        "_id": ambulance_id,
        "driver_name": data.driver_name,
        "ambulance_number": data.ambulance_number,
        "password_hash": hash_password(data.password),
        "created_at": datetime.utcnow()
    }
    
    db.ambulances.insert_one(ambulance_doc)
    log.info(f"✅ Ambulance registered: {data.ambulance_number}")
    
    # Create access token
    token = create_access_token({
        "sub": ambulance_id,
        "role": "ambulance",
        "ambulance_number": data.ambulance_number
    })
    
    return TokenResponse(
        access_token=token,
        role="ambulance",
        user_data={
            "id": ambulance_id,
            "driver_name": data.driver_name,
            "ambulance_number": data.ambulance_number
        }
    )


@router.post("/ambulance/login", response_model=TokenResponse)
async def ambulance_login(data: AmbulanceLogin):
    """Login for ambulance."""
    db = get_db()
    
    # Find ambulance
    ambulance = db.ambulances.find_one({"ambulance_number": data.ambulance_number})
    if not ambulance:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ambulance number or password"
        )
    
    # Verify password
    if not verify_password(data.password, ambulance["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ambulance number or password"
        )
    
    log.info(f"✅ Ambulance logged in: {data.ambulance_number}")
    
    # Create access token
    token = create_access_token({
        "sub": ambulance["_id"],
        "role": "ambulance",
        "ambulance_number": data.ambulance_number
    })
    
    return TokenResponse(
        access_token=token,
        role="ambulance",
        user_data={
            "id": ambulance["_id"],
            "driver_name": ambulance["driver_name"],
            "ambulance_number": ambulance["ambulance_number"]
        }
    )


# ============ HOSPITAL ROUTES ============
@router.post("/hospital/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def hospital_signup(data: HospitalSignup):
    """Register a new hospital."""
    db = get_db()
    
    # Generate unique hospital ID
    hospital_id = generate_hospital_id(data.address)
    
    # Ensure uniqueness
    while db.hospitals.find_one({"hospital_id": hospital_id}):
        hospital_id = generate_hospital_id(data.address)
    
    # Create hospital record
    hospital_doc = {
        "hospital_id": hospital_id,
        "hospital_name": data.hospital_name,
        "address": data.address,
        "password_hash": hash_password(data.password),
        "created_at": datetime.utcnow()
    }
    
    db.hospitals.insert_one(hospital_doc)
    log.info(f"✅ Hospital registered: {hospital_id} - {data.hospital_name}")
    
    # Create access token
    token = create_access_token({
        "sub": hospital_id,
        "role": "hospital",
        "hospital_id": hospital_id
    })
    
    return TokenResponse(
        access_token=token,
        role="hospital",
        user_data={
            "hospital_id": hospital_id,
            "hospital_name": data.hospital_name,
            "address": data.address
        }
    )


@router.post("/hospital/login", response_model=TokenResponse)
async def hospital_login(data: HospitalLogin):
    """Login for hospital."""
    db = get_db()
    
    # Find hospital
    hospital = db.hospitals.find_one({"hospital_id": data.hospital_id})
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid hospital ID or password"
        )
    
    # Verify password
    if not verify_password(data.password, hospital["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid hospital ID or password"
        )
    
    log.info(f"✅ Hospital logged in: {data.hospital_id}")
    
    # Create access token
    token = create_access_token({
        "sub": hospital["hospital_id"],
        "role": "hospital",
        "hospital_id": data.hospital_id
    })
    
    return TokenResponse(
        access_token=token,
        role="hospital",
        user_data={
            "hospital_id": hospital["hospital_id"],
            "hospital_name": hospital["hospital_name"],
            "address": hospital["address"]
        }
    )


# ============ CASE ROUTES ============
@router.post("/send-case", response_model=CaseResponse)
async def send_case(data: CaseCreate, current_user: dict = Depends(require_ambulance)):
    """Send a case from ambulance (requires ambulance auth)."""
    db = get_db()
    
    # Get ambulance details
    ambulance = db.ambulances.find_one({"_id": current_user["user_id"]})
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance not found")
    
    # Create case
    case_id = str(uuid.uuid4())
    case_doc = {
        "case_id": case_id,
        "ambulance_number": ambulance["ambulance_number"],
        "driver_name": ambulance["driver_name"],
        "patient_data": data.patient_data,
        "severity": data.severity,
        "confidence": data.confidence,
        "timestamp": datetime.utcnow(),
        "status": "pending"
    }
    
    db.cases.insert_one(case_doc)
    log.info(f"✅ Case created: {case_id} - Severity: {data.severity}")
    
    return CaseResponse(**case_doc)


@router.get("/cases")
async def get_cases(
    limit: int = 50,
    current_user: dict = Depends(require_hospital)
):
    """Get all cases (requires hospital auth)."""
    db = get_db()
    
    cases = list(db.cases.find().sort("timestamp", -1).limit(limit))
    
    # Convert MongoDB documents to response format
    result = []
    for case in cases:
        case["_id"] = str(case["_id"])
        result.append(case)
    
    log.info(f"✅ Retrieved {len(result)} cases for hospital")
    return result


@router.get("/ambulance/recent-cases")
async def get_ambulance_cases(
    limit: int = 5,
    current_user: dict = Depends(require_ambulance)
):
    """Get recent cases for current ambulance."""
    db = get_db()
    
    ambulance = db.ambulances.find_one({"_id": current_user["user_id"]})
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance not found")
    
    cases = list(
        db.cases.find({"ambulance_number": ambulance["ambulance_number"]})
        .sort("timestamp", -1)
        .limit(limit)
    )
    
    # Convert MongoDB documents
    result = []
    for case in cases:
        case["_id"] = str(case["_id"])
        result.append(case)
    
    return result


@router.get("/hospital/stats")
async def get_hospital_stats(current_user: dict = Depends(require_hospital)):
    """Get severity statistics for hospital dashboard."""
    db = get_db()
    
    # Aggregate severity counts
    pipeline = [
        {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
    ]
    
    results = list(db.cases.aggregate(pipeline))
    
    stats = {
        "Immediate": 0,
        "Urgent": 0,
        "Moderate": 0,
        "Minor": 0,
        "total": 0
    }
    
    for item in results:
        severity = item["_id"]
        count = item["count"]
        if severity in stats:
            stats[severity] = count
            stats["total"] += count
    
    return stats
