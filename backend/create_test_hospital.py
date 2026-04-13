#!/usr/bin/env python3
"""Create a test hospital with proper password hash for testing"""
from pymongo import MongoClient
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = MongoClient('mongodb://localhost:27017/')['triage_system']

# Create test hospital
hospital_id = "HOSP-TEST-1234"
password_hash = pwd_context.hash("hospital123")

hospital = {
    "hospital_id": hospital_id,
    "hospital_name": "Test Hospital for ICU",
    "address": "Chennai, India",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "available_beds": 50,
    "current_load": 20,
    "icu_total": 20,
    "icu_available": 8,
    "icu_occupied": 12,
    "occupancy_rate": 60.0,
    "password_hash": password_hash,
    "created_at": datetime.utcnow()
}

# Delete if exists
db.hospitals.delete_one({"hospital_id": hospital_id})

# Insert
db.hospitals.insert_one(hospital)

print(f"✅ Created test hospital: {hospital_id}")
print(f"   Password: hospital123")
print(f"   ICU: {hospital['icu_available']}/{hospital['icu_total']}")
