# backend/app/database.py
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from loguru import logger as log
from typing import Optional
import os

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017/"
DB_NAME = "triage_system"

client: Optional[MongoClient] = None
db = None


def connect_db():
    """Initialize MongoDB connection."""
    global client, db
    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Create indexes
        db.ambulances.create_index([("ambulance_number", ASCENDING)], unique=True)
        db.hospitals.create_index([("hospital_id", ASCENDING)], unique=True)
        db.cases.create_index([("case_id", ASCENDING)], unique=True)
        db.cases.create_index([("timestamp", ASCENDING)])
        
        log.info(f"✅ Connected to MongoDB: {DB_NAME}")
    except Exception as e:
        log.error(f"❌ MongoDB connection failed: {e}")
        raise


def disconnect_db():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        log.info("🛑 MongoDB connection closed")


def get_db():
    """Get database instance."""
    if db is None:
        connect_db()
    return db
