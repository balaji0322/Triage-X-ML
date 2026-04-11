# backend/app/auth_schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


# ============ AMBULANCE SCHEMAS ============
class AmbulanceSignup(BaseModel):
    driver_name: str = Field(..., min_length=2, max_length=100)
    ambulance_number: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class AmbulanceLogin(BaseModel):
    ambulance_number: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6)


class AmbulanceResponse(BaseModel):
    id: str
    driver_name: str
    ambulance_number: str


# ============ HOSPITAL SCHEMAS ============
class HospitalSignup(BaseModel):
    hospital_name: str = Field(..., min_length=3, max_length=200)
    address: str = Field(..., min_length=5, max_length=500)
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class HospitalLogin(BaseModel):
    hospital_id: str = Field(..., min_length=5, max_length=20)
    password: str = Field(..., min_length=6)


class HospitalResponse(BaseModel):
    hospital_id: str
    hospital_name: str
    address: str


# ============ AUTH RESPONSE ============
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_data: dict


# ============ CASE SCHEMAS ============
class CaseCreate(BaseModel):
    patient_data: dict
    severity: str
    confidence: float


class CaseResponse(BaseModel):
    case_id: str
    ambulance_number: str
    driver_name: str
    patient_data: dict
    severity: str
    confidence: float
    timestamp: datetime
    status: str = "pending"
