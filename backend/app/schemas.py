# backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import Literal, Optional


class PatientInput(BaseModel):
    heart_rate: int = Field(..., ge=30, le=250, description="beats per minute")
    systolic_bp: int = Field(..., ge=50, le=250, description="mmHg")
    diastolic_bp: int = Field(..., ge=30, le=150, description="mmHg")
    oxygen_saturation: int = Field(..., ge=50, le=100, description="%")
    temperature: float = Field(..., ge=30, le=45, description="°C")
    respiratory_rate: int = Field(..., ge=5, le=60, description="breaths per minute")
    chest_pain: Literal[0, 1] = Field(..., description="0 = no, 1 = yes")
    fever: Literal[0, 1] = Field(..., description="0 = no, 1 = yes")
    breathing_difficulty: Literal[0, 1] = Field(..., description="0 = no, 1 = yes")
    injury_type: Literal[0, 1] = Field(..., description="0 = none, 1 = traumatic")
    diabetes: Literal[0, 1] = Field(..., description="0 = no, 1 = yes")
    heart_disease: Literal[0, 1] = Field(..., description="0 = no, 1 = yes")
    hypertension: Literal[0, 1] = Field(..., description="0 = no, 1 = yes")
    asthma: Literal[0, 1] = Field(..., description="0 = no, 1 = yes")
    age: int = Field(..., ge=0, le=120, description="years")
    gender: Literal["male", "female", "other"] = Field(...)


class PredictionResponse(BaseModel):
    severity: str
    confidence: float  # probability of the predicted class
    severity_code: int  # 0‑3 (same order as UI)
