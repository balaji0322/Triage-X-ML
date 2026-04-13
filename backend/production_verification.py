#!/usr/bin/env python3
"""
TRIAGE-X Production Verification Script
Verifies all system components are properly connected and functional
"""
import sys
import asyncio
from pathlib import Path
from loguru import logger as log

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

def verify_ml_model():
    """Verify ML model is loaded and functional."""
    log.info("🧠 Verifying ML Model...")
    
    try:
        from app.utils import load_artifacts
        model, label_map, feature_importance = load_artifacts()
        
        assert model is not None, "Model not loaded"
        assert label_map is not None, "Label map not loaded"
        assert feature_importance is not None, "Feature importance not loaded"
        
        log.success("✅ ML Model loaded successfully")
        log.info(f"   - Label map: {label_map}")
        log.info(f"   - Feature importance: {len(feature_importance)} features")
        
        return True
    except Exception as e:
        log.error(f"❌ ML Model verification failed: {e}")
        return False


def verify_database():
    """Verify MongoDB connection and indexes."""
    log.info("🗄️  Verifying Database...")
    
    try:
        from app.database import connect_db, get_db
        
        connect_db()
        db = get_db()
        
        # Check collections
        collections = db.list_collection_names()
        required_collections = ['ambulances', 'hospitals', 'cases']
        
        for coll in required_collections:
            if coll not in collections:
                db.create_collection(coll)
                log.info(f"   - Created collection: {coll}")
        
        # Verify indexes
        ambulance_indexes = list(db.ambulances.list_indexes())
        hospital_indexes = list(db.hospitals.list_indexes())
        case_indexes = list(db.cases.list_indexes())
        
        log.success("✅ Database connected successfully")
        log.info(f"   - Ambulances: {len(ambulance_indexes)} indexes")
        log.info(f"   - Hospitals: {len(hospital_indexes)} indexes")
        log.info(f"   - Cases: {len(case_indexes)} indexes")
        
        return True
    except Exception as e:
        log.error(f"❌ Database verification failed: {e}")
        return False


def verify_prediction():
    """Verify prediction endpoint works correctly."""
    log.info("🔮 Verifying Prediction System...")
    
    try:
        from app.utils import load_artifacts
        import pandas as pd
        
        model, label_map, _ = load_artifacts()
        
        # Test patient data
        test_data = {
            'heart_rate': 110,
            'systolic_bp': 85,
            'diastolic_bp': 60,
            'oxygen_saturation': 88,
            'temperature': 39.2,
            'respiratory_rate': 28,
            'age': 75,
            'chest_pain': 1,
            'fever': 1,
            'breathing_difficulty': 1,
            'injury_type': 0,
            'diabetes': 1,
            'heart_disease': 1,
            'hypertension': 1,
            'asthma': 0,
            'gender': 'male'
        }
        
        # Create DataFrame and add derived features
        df = pd.DataFrame([test_data])
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
        
        log.success("✅ Prediction system working")
        log.info(f"   - Test prediction: {pred_name} ({confidence:.2%} confidence)")
        
        return True
    except Exception as e:
        log.error(f"❌ Prediction verification failed: {e}")
        return False


def verify_authentication():
    """Verify authentication system."""
    log.info("🔐 Verifying Authentication...")
    
    try:
        from app.auth import hash_password, verify_password, create_access_token, decode_token
        
        # Test password hashing
        password = "test_password_123"
        hashed = hash_password(password)
        assert verify_password(password, hashed), "Password verification failed"
        
        # Test JWT token
        token_data = {"sub": "test_user", "role": "ambulance"}
        token = create_access_token(token_data)
        decoded = decode_token(token)
        assert decoded["sub"] == "test_user", "Token decode failed"
        
        log.success("✅ Authentication system working")
        log.info("   - Password hashing: OK")
        log.info("   - JWT tokens: OK")
        
        return True
    except Exception as e:
        log.error(f"❌ Authentication verification failed: {e}")
        return False


def verify_websocket():
    """Verify WebSocket manager."""
    log.info("📡 Verifying WebSocket System...")
    
    try:
        from app.websocket_manager import manager
        
        # Check manager is initialized
        assert manager is not None, "WebSocket manager not initialized"
        
        hospital_count = manager.get_connection_count('hospital')
        ambulance_count = manager.get_connection_count('ambulance')
        
        log.success("✅ WebSocket system initialized")
        log.info(f"   - Hospital connections: {hospital_count}")
        log.info(f"   - Ambulance connections: {ambulance_count}")
        
        return True
    except Exception as e:
        log.error(f"❌ WebSocket verification failed: {e}")
        return False


def verify_advanced_features():
    """Verify advanced features are available."""
    log.info("🚀 Verifying Advanced Features...")
    
    try:
        from app.advanced_features import calculate_distance, calculate_priority_score
        
        # Test distance calculation
        distance = calculate_distance(13.0827, 80.2707, 12.9716, 77.5946)
        assert distance > 0, "Distance calculation failed"
        
        # Test priority score
        score = calculate_priority_score(0, 10.5, 5)
        assert score > 0, "Priority score calculation failed"
        
        log.success("✅ Advanced features working")
        log.info(f"   - Distance calculation: {distance:.2f} km")
        log.info(f"   - Priority scoring: {score:.2f}")
        
        return True
    except Exception as e:
        log.error(f"❌ Advanced features verification failed: {e}")
        return False


def verify_api_endpoints():
    """Verify all API endpoints are registered."""
    log.info("🌐 Verifying API Endpoints...")
    
    try:
        from app.main import app
        
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                for method in route.methods:
                    if method != 'HEAD':
                        routes.append(f"{method} {route.path}")
        
        required_endpoints = [
            'POST /predict',
            'POST /api/ambulance/signup',
            'POST /api/ambulance/login',
            'POST /api/hospital/signup',
            'POST /api/hospital/login',
            'POST /api/send-case',
            'GET /api/cases',
            'GET /api/hospital/stats',
            'POST /api/suggest-hospital',
            'POST /api/predict/enhanced',
            'GET /api/analytics',
        ]
        
        missing = []
        for endpoint in required_endpoints:
            if endpoint not in routes:
                missing.append(endpoint)
        
        if missing:
            log.warning(f"⚠️  Missing endpoints: {missing}")
        
        log.success("✅ API endpoints registered")
        log.info(f"   - Total routes: {len(routes)}")
        log.info(f"   - Required endpoints: {len(required_endpoints) - len(missing)}/{len(required_endpoints)}")
        
        return len(missing) == 0
    except Exception as e:
        log.error(f"❌ API endpoint verification failed: {e}")
        return False


def main():
    """Run all verification checks."""
    log.info("=" * 60)
    log.info("🚀 TRIAGE-X PRODUCTION VERIFICATION")
    log.info("=" * 60)
    
    checks = [
        ("ML Model", verify_ml_model),
        ("Database", verify_database),
        ("Prediction", verify_prediction),
        ("Authentication", verify_authentication),
        ("WebSocket", verify_websocket),
        ("Advanced Features", verify_advanced_features),
        ("API Endpoints", verify_api_endpoints),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            log.error(f"❌ {name} check crashed: {e}")
            results[name] = False
        log.info("")
    
    # Summary
    log.info("=" * 60)
    log.info("📊 VERIFICATION SUMMARY")
    log.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        log.info(f"{status} - {name}")
    
    log.info("=" * 60)
    log.info(f"Result: {passed}/{total} checks passed")
    
    if passed == total:
        log.success("🎉 ALL SYSTEMS OPERATIONAL - PRODUCTION READY!")
        return 0
    else:
        log.error("⚠️  SOME CHECKS FAILED - REVIEW REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
