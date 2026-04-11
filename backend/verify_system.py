#!/usr/bin/env python3
"""
System Verification Script for Triage-X
Verifies all components are properly connected and working.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def verify_ml_model():
    """Verify ML model can be loaded and used."""
    print("\n🧠 Verifying ML Model...")
    try:
        from app.utils import load_artifacts
        model, label_map, feature_imp = load_artifacts()
        print(f"   ✅ Model loaded successfully")
        print(f"   ✅ Label map: {label_map}")
        print(f"   ✅ Feature importance: {len(feature_imp)} features")
        return True
    except Exception as e:
        print(f"   ❌ Model loading failed: {e}")
        return False

def verify_database():
    """Verify MongoDB connection."""
    print("\n🗄️  Verifying Database Connection...")
    try:
        from app.database import get_db
        db = get_db()
        
        # Test connection
        db.command('ping')
        print(f"   ✅ MongoDB connected: {db.name}")
        
        # Check collections
        collections = db.list_collection_names()
        print(f"   ✅ Collections: {collections}")
        
        # Check indexes
        for coll_name in ['ambulances', 'hospitals', 'cases']:
            if coll_name in collections:
                indexes = list(db[coll_name].list_indexes())
                print(f"   ✅ {coll_name} indexes: {len(indexes)}")
        
        return True
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False

def verify_auth():
    """Verify authentication functions."""
    print("\n🔐 Verifying Authentication...")
    try:
        from app.auth import hash_password, verify_password, create_access_token, decode_token
        
        # Test password hashing
        password = "test123"
        hashed = hash_password(password)
        assert verify_password(password, hashed), "Password verification failed"
        print(f"   ✅ Password hashing works")
        
        # Test JWT
        token = create_access_token({"sub": "test_user", "role": "ambulance"})
        payload = decode_token(token)
        assert payload["sub"] == "test_user", "JWT decode failed"
        print(f"   ✅ JWT token generation works")
        
        return True
    except Exception as e:
        print(f"   ❌ Authentication verification failed: {e}")
        return False

def verify_prediction():
    """Verify prediction endpoint logic."""
    print("\n🔮 Verifying Prediction Logic...")
    try:
        from app.schemas import PatientInput
        from app.utils import load_artifacts
        import pandas as pd
        import json
        
        # Test patient data
        test_data = {
            "heart_rate": 110,
            "systolic_bp": 140,
            "diastolic_bp": 90,
            "oxygen_saturation": 92,
            "temperature": 38.5,
            "respiratory_rate": 24,
            "chest_pain": 1,
            "fever": 1,
            "breathing_difficulty": 1,
            "injury_type": 0,
            "diabetes": 0,
            "heart_disease": 1,
            "hypertension": 0,
            "asthma": 0,
            "age": 65,
            "gender": "male"
        }
        
        # Validate with Pydantic
        patient = PatientInput(**test_data)
        print(f"   ✅ Patient data validation works")
        
        # Test prediction
        model, label_map, _ = load_artifacts()
        df = pd.DataFrame([json.loads(patient.model_dump_json())])
        
        # Add derived features (same as in main.py)
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
        
        probs = model.predict_proba(df)[0]
        pred_index = int(probs.argmax())
        pred_name = label_map[str(pred_index)]
        confidence = float(probs[pred_index])
        
        print(f"   ✅ Prediction works: {pred_name} ({confidence:.2%})")
        
        return True
    except Exception as e:
        print(f"   ❌ Prediction verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_routes():
    """Verify all required routes are defined."""
    print("\n🛣️  Verifying API Routes...")
    try:
        from app.main import app
        
        routes = [route.path for route in app.routes]
        
        required_routes = [
            "/api/ambulance/signup",
            "/api/ambulance/login",
            "/api/hospital/signup",
            "/api/hospital/login",
            "/predict",
            "/api/send-case",
            "/api/cases",
            "/api/ambulance/recent-cases",
            "/api/hospital/stats",
            "/ping"
        ]
        
        for route in required_routes:
            if route in routes:
                print(f"   ✅ {route}")
            else:
                print(f"   ❌ {route} - MISSING")
                return False
        
        return True
    except Exception as e:
        print(f"   ❌ Route verification failed: {e}")
        return False

def main():
    """Run all verifications."""
    print("=" * 70)
    print("🔍 TRIAGE-X SYSTEM VERIFICATION")
    print("=" * 70)
    
    results = {
        "ML Model": verify_ml_model(),
        "Database": verify_database(),
        "Authentication": verify_auth(),
        "Prediction": verify_prediction(),
        "API Routes": verify_routes()
    }
    
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component}: {'PASS' if status else 'FAIL'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All verifications passed! System is ready.")
        return 0
    else:
        print("\n⚠️  Some verifications failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
