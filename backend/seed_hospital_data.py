#!/usr/bin/env python3
"""
Seed Hospital Data with GPS Coordinates
Adds real location data to existing hospitals
"""
from pymongo import MongoClient
from loguru import logger as log

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017/"
DB_NAME = "triage_system"

# Real hospital coordinates (major cities in India)
HOSPITAL_DATA = [
    {
        "city": "Chennai",
        "hospitals": [
            {"name": "Apollo Hospital", "lat": 13.0358, "lng": 80.2464, "beds": 50, "load": 15},
            {"name": "Fortis Malar Hospital", "lat": 13.0569, "lng": 80.2425, "beds": 40, "load": 20},
            {"name": "MIOT International", "lat": 13.0108, "lng": 80.2100, "beds": 60, "load": 25},
            {"name": "Kauvery Hospital", "lat": 13.0475, "lng": 80.2533, "beds": 35, "load": 10},
            {"name": "Gleneagles Global", "lat": 13.0878, "lng": 80.2785, "beds": 45, "load": 18},
        ]
    },
    {
        "city": "Bangalore",
        "hospitals": [
            {"name": "Manipal Hospital", "lat": 12.9698, "lng": 77.6489, "beds": 55, "load": 22},
            {"name": "Fortis Hospital", "lat": 12.9352, "lng": 77.6245, "beds": 48, "load": 19},
            {"name": "Columbia Asia", "lat": 12.9716, "lng": 77.5946, "beds": 42, "load": 16},
        ]
    },
    {
        "city": "Mumbai",
        "hospitals": [
            {"name": "Lilavati Hospital", "lat": 19.0560, "lng": 72.8347, "beds": 65, "load": 30},
            {"name": "Breach Candy Hospital", "lat": 18.9667, "lng": 72.8081, "beds": 50, "load": 25},
            {"name": "Hinduja Hospital", "lat": 19.0176, "lng": 72.8562, "beds": 70, "load": 35},
        ]
    },
    {
        "city": "Delhi",
        "hospitals": [
            {"name": "Max Super Speciality", "lat": 28.5355, "lng": 77.3910, "beds": 60, "load": 28},
            {"name": "Fortis Escorts", "lat": 28.6139, "lng": 77.2090, "beds": 55, "load": 24},
            {"name": "Apollo Hospital", "lat": 28.5672, "lng": 77.2100, "beds": 75, "load": 32},
        ]
    }
]


def seed_hospitals():
    """Add GPS coordinates and capacity data to hospitals."""
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    log.info("🌱 Starting hospital data seeding...")
    
    updated_count = 0
    created_count = 0
    
    for city_data in HOSPITAL_DATA:
        city = city_data["city"]
        log.info(f"📍 Processing {city} hospitals...")
        
        for hospital_data in city_data["hospitals"]:
            # Check if hospital exists by name
            existing = db.hospitals.find_one({"hospital_name": hospital_data["name"]})
            
            if existing:
                # Update existing hospital
                result = db.hospitals.update_one(
                    {"_id": existing["_id"]},
                    {
                        "$set": {
                            "latitude": hospital_data["lat"],
                            "longitude": hospital_data["lng"],
                            "available_beds": hospital_data["beds"],
                            "current_load": hospital_data["load"],
                            "city": city
                        }
                    }
                )
                if result.modified_count > 0:
                    updated_count += 1
                    log.info(f"  ✅ Updated: {hospital_data['name']}")
            else:
                # Create new hospital
                from datetime import datetime
                import uuid
                
                # Generate hospital ID
                city_code = city[:3].upper()
                hospital_id = f"HOSP-{city_code}-{str(uuid.uuid4().int)[:4]}"
                
                hospital_doc = {
                    "hospital_id": hospital_id,
                    "hospital_name": hospital_data["name"],
                    "address": f"{city}, India",
                    "latitude": hospital_data["lat"],
                    "longitude": hospital_data["lng"],
                    "available_beds": hospital_data["beds"],
                    "current_load": hospital_data["load"],
                    "city": city,
                    "password_hash": "$2b$12$dummy_hash_for_seeded_hospitals",  # Placeholder
                    "created_at": datetime.utcnow()
                }
                
                db.hospitals.insert_one(hospital_doc)
                created_count += 1
                log.info(f"  ✅ Created: {hospital_data['name']} ({hospital_id})")
    
    # Create index on location fields
    db.hospitals.create_index([("latitude", 1), ("longitude", 1)])
    
    log.success(f"🎉 Seeding complete!")
    log.info(f"   - Updated: {updated_count} hospitals")
    log.info(f"   - Created: {created_count} hospitals")
    log.info(f"   - Total: {updated_count + created_count} hospitals with GPS data")
    
    client.close()


if __name__ == "__main__":
    seed_hospitals()
