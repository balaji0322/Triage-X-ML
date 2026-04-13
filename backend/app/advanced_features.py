# backend/app/advanced_features.py
"""
Advanced Features for Triage-X System
- Smart Hospital Allocation
- Enhanced AI Insights
- Analytics Dashboard
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from loguru import logger as log
from datetime import datetime, timedelta
import math

from .auth import require_ambulance, require_hospital, get_current_user
from .database import get_db
from .utils import load_artifacts

router = APIRouter()


# ============ SCHEMAS ============

class HospitalAllocationRequest(BaseModel):
    """Request for smart hospital allocation."""
    severity: str = Field(..., description="Patient severity level")
    severity_code: int = Field(..., ge=0, le=2, description="Severity code (0=Urgent, 1=Moderate, 2=Minor)")
    ambulance_lat: Optional[float] = Field(default=13.0827, description="Ambulance latitude")
    ambulance_lon: Optional[float] = Field(default=80.2707, description="Ambulance longitude")


class HospitalAllocationResponse(BaseModel):
    """Response with suggested hospital."""
    suggested_hospital_id: str
    hospital_name: str
    distance_km: float
    current_load: int
    priority_score: float
    reason: str
    alternatives: List[Dict]


class EnhancedPredictionResponse(BaseModel):
    """Enhanced prediction with AI insights."""
    severity: str
    severity_code: int
    confidence: float
    risk_score: int  # 0-100
    top_factors: List[Dict[str, any]]
    recommendation: str


class AnalyticsResponse(BaseModel):
    """Analytics dashboard data."""
    total_cases: int
    cases_by_severity: Dict[str, int]
    peak_hours: List[Dict]
    average_severity_score: float
    cases_last_24h: int
    trend: str


# ============ FEATURE 2: SMART HOSPITAL ALLOCATION ============

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula."""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


def calculate_priority_score(severity_code: int, distance_km: float, load: int) -> float:
    """
    Calculate hospital priority score.
    Lower score = better choice
    
    Weights:
    - Severity: 40% (more urgent = need closer hospital)
    - Distance: 35% (closer is better)
    - Load: 25% (less load is better)
    """
    # Severity weight (0=Urgent needs closest, 2=Minor can go farther)
    severity_weight = (2 - severity_code) * 40  # Urgent=80, Moderate=40, Minor=0
    
    # Distance weight (normalized to 0-35 range, assuming max 50km)
    distance_weight = min(distance_km / 50 * 35, 35)
    
    # Load weight (normalized to 0-25 range, assuming max 100 cases)
    load_weight = min(load / 100 * 25, 25)
    
    total_score = severity_weight + distance_weight + load_weight
    return round(total_score, 2)


@router.post("/suggest-hospital", response_model=HospitalAllocationResponse)
async def suggest_hospital(
    request: HospitalAllocationRequest,
    current_user: dict = Depends(require_ambulance)
):
    """
    🏥 FEATURE 2: Smart Hospital Allocation
    
    Suggests the best hospital based on:
    - Patient severity
    - Distance from ambulance
    - Hospital current load
    """
    db = get_db()
    
    try:
        # Get all hospitals with their coordinates (simulated)
        hospitals = list(db.hospitals.find())
        
        if not hospitals:
            raise HTTPException(status_code=404, detail="No hospitals found in system")
        
        # Simulate hospital coordinates (in production, these would be in DB)
        hospital_coords = {
            "HOSP": (13.0827, 80.2707),  # Chennai
            "HOSP-CHE": (13.0827, 80.2707),
            "HOSP-BAN": (12.9716, 77.5946),  # Bangalore
            "HOSP-MUM": (19.0760, 72.8777),  # Mumbai
            "HOSP-DEL": (28.7041, 77.1025),  # Delhi
        }
        
        hospital_scores = []
        
        for hospital in hospitals:
            hospital_id = hospital["hospital_id"]
            
            # Get hospital coordinates (default to Chennai if not found)
            coords = hospital_coords.get(
                hospital_id[:8],  # Match prefix
                (13.0827, 80.2707)
            )
            
            # Calculate distance
            distance = calculate_distance(
                request.ambulance_lat,
                request.ambulance_lon,
                coords[0],
                coords[1]
            )
            
            # Get current hospital load (number of pending cases)
            load = db.cases.count_documents({
                "hospital_assigned": hospital_id,
                "status": "pending"
            })
            
            # Calculate priority score
            priority = calculate_priority_score(
                request.severity_code,
                distance,
                load
            )
            
            hospital_scores.append({
                "hospital_id": hospital_id,
                "hospital_name": hospital["hospital_name"],
                "distance_km": distance,
                "current_load": load,
                "priority_score": priority,
                "coordinates": coords
            })
        
        # Sort by priority score (lower is better)
        hospital_scores.sort(key=lambda x: x["priority_score"])
        
        best_hospital = hospital_scores[0]
        alternatives = hospital_scores[1:4]  # Top 3 alternatives
        
        # Generate reason
        reason = f"Best match: {best_hospital['distance_km']}km away, {best_hospital['current_load']} active cases"
        if request.severity_code == 0:  # Urgent
            reason += ". URGENT case - closest available hospital selected."
        
        log.info(f"✅ Hospital suggested: {best_hospital['hospital_id']} for {request.severity} case")
        
        return HospitalAllocationResponse(
            suggested_hospital_id=best_hospital["hospital_id"],
            hospital_name=best_hospital["hospital_name"],
            distance_km=best_hospital["distance_km"],
            current_load=best_hospital["current_load"],
            priority_score=best_hospital["priority_score"],
            reason=reason,
            alternatives=[
                {
                    "hospital_id": h["hospital_id"],
                    "hospital_name": h["hospital_name"],
                    "distance_km": h["distance_km"],
                    "load": h["current_load"]
                }
                for h in alternatives
            ]
        )
        
    except Exception as e:
        log.error(f"❌ Hospital allocation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Allocation error: {str(e)}")


# ============ FEATURE 3: ENHANCED AI INSIGHTS ============

@router.post("/predict/enhanced", response_model=EnhancedPredictionResponse)
async def enhanced_prediction(payload: dict):
    """
    🧠 FEATURE 3: Enhanced AI Insights
    
    Provides prediction with:
    - Risk score (0-100)
    - Top contributing factors
    - Actionable recommendations
    """
    try:
        # Load model and feature importance
        model, label_map, feature_importance = load_artifacts()
        
        # Get base prediction (reuse existing logic)
        import pandas as pd
        df = pd.DataFrame([payload])
        
        # Add derived features
        df['pulse_pressure'] = df['systolic_bp'] - df['diastolic_bp']
        df['mean_arterial_pressure'] = df['diastolic_bp'] + (df['pulse_pressure'] / 3)
        df['shock_index'] = df['heart_rate'] / df['systolic_bp']
        df['age_risk'] = (df['age'] > 65).astype(int)
        df['has_fever'] = (df['temperature'] > 38.0).astype(int)
        df['hypoxia'] = (df['oxygen_saturation'] < 92).astype(int)
        df['tachycardia'] = (df['heart_rate'] > 100).astype(int)
        df['tachypnea'] = (df['respiratory_rate'] > 20).astype(int)
        df['hypotension'] = (df['systolic_bp'] < 90).astype(int)
        df['comorbidity_count'] = (
            df['diabetes'] + df['heart_disease'] + 
            df['hypertension'] + df['asthma']
        )
        df['critical_symptoms'] = (
            df['chest_pain'] + df['breathing_difficulty'] + 
            df['injury_type']
        )
        
        # Predict
        probs = model.predict_proba(df)[0]
        pred_index = int(probs.argmax())
        pred_name = label_map[str(pred_index)]
        confidence = float(probs[pred_index])
        
        # Calculate risk score (0-100)
        risk_score = int(confidence * 100)
        
        # Get top contributing factors from feature importance
        top_features = sorted(
            feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:3]
        
        top_factors = [
            {
                "feature": feat.replace("num__", "").replace("cat__", ""),
                "importance": round(float(imp), 4),
                "value": payload.get(feat.replace("num__", "").replace("cat__", ""), "N/A")
            }
            for feat, imp in top_features
        ]
        
        # Generate recommendation
        recommendations = {
            "Urgent": "🚨 IMMEDIATE ATTENTION REQUIRED. Prepare emergency protocols.",
            "Moderate": "⚠️ Monitor closely. Prepare for potential escalation.",
            "Minor": "✅ Standard care. Continue monitoring vitals."
        }
        recommendation = recommendations.get(pred_name, "Monitor patient condition")
        
        log.info(f"✅ Enhanced prediction: {pred_name} (Risk: {risk_score})")
        
        return EnhancedPredictionResponse(
            severity=pred_name,
            severity_code=pred_index,
            confidence=round(confidence, 4),
            risk_score=risk_score,
            top_factors=top_factors,
            recommendation=recommendation
        )
        
    except Exception as e:
        log.error(f"❌ Enhanced prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


# ============ FEATURE 4: ADMIN ANALYTICS DASHBOARD ============

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(current_user: dict = Depends(require_hospital)):
    """
    📊 FEATURE 4: Admin Analytics Dashboard
    
    Provides comprehensive analytics:
    - Total cases and breakdown by severity
    - Peak hours analysis
    - Average severity score
    - 24-hour trends
    """
    db = get_db()
    
    try:
        # Total cases
        total_cases = db.cases.count_documents({})
        
        # Cases by severity
        severity_pipeline = [
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
        ]
        severity_results = list(db.cases.aggregate(severity_pipeline))
        cases_by_severity = {item["_id"]: item["count"] for item in severity_results}
        
        # Peak hours (group by hour of day)
        peak_hours_pipeline = [
            {
                "$project": {
                    "hour": {"$hour": "$timestamp"}
                }
            },
            {
                "$group": {
                    "_id": "$hour",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        peak_results = list(db.cases.aggregate(peak_hours_pipeline))
        peak_hours = [
            {"hour": item["_id"], "cases": item["count"]}
            for item in peak_results
        ]
        
        # Average severity score (Urgent=3, Moderate=2, Minor=1)
        severity_scores = {
            "Urgent": 3,
            "Moderate": 2,
            "Minor": 1
        }
        total_score = sum(
            severity_scores.get(sev, 0) * count
            for sev, count in cases_by_severity.items()
        )
        avg_severity = round(total_score / total_cases, 2) if total_cases > 0 else 0
        
        # Cases in last 24 hours
        last_24h = datetime.utcnow() - timedelta(hours=24)
        cases_last_24h = db.cases.count_documents({
            "timestamp": {"$gte": last_24h}
        })
        
        # Trend analysis
        last_48h = datetime.utcnow() - timedelta(hours=48)
        cases_24_48h = db.cases.count_documents({
            "timestamp": {"$gte": last_48h, "$lt": last_24h}
        })
        
        if cases_24_48h > 0:
            trend_pct = ((cases_last_24h - cases_24_48h) / cases_24_48h) * 100
            if trend_pct > 10:
                trend = f"📈 Increasing ({trend_pct:+.1f}%)"
            elif trend_pct < -10:
                trend = f"📉 Decreasing ({trend_pct:+.1f}%)"
            else:
                trend = "➡️ Stable"
        else:
            trend = "📊 Insufficient data"
        
        log.info(f"✅ Analytics generated: {total_cases} total cases")
        
        return AnalyticsResponse(
            total_cases=total_cases,
            cases_by_severity=cases_by_severity,
            peak_hours=peak_hours,
            average_severity_score=avg_severity,
            cases_last_24h=cases_last_24h,
            trend=trend
        )
        
    except Exception as e:
        log.error(f"❌ Analytics generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")
