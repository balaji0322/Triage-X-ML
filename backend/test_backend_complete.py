#!/usr/bin/env python3
"""
Complete backend verification test.
Tests all endpoints and logging functionality.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    try:
        from app.logger import log
        from app.utils import load_artifacts, severity_code_to_name, get_color
        from app.schemas import PatientInput, PredictionResponse
        from app.main import app
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_logger():
    """Test logger configuration."""
    print("\n🧪 Testing logger...")
    try:
        from app.logger import log
        log.debug("Debug message")
        log.info("Info message")
        log.warning("Warning message")
        log.error("Error message")
        print("✅ Logger working correctly")
        return True
    except Exception as e:
        print(f"❌ Logger test failed: {e}")
        return False

def test_model_loading():
    """Test model artifact loading."""
    print("\n🧪 Testing model loading...")
    try:
        from app.utils import load_artifacts
        model, label_map, feature_importance = load_artifacts()
        
        print(f"   Model type: {type(model).__name__}")
        print(f"   Label map: {label_map}")
        print(f"   Feature importance: {len(feature_importance)} features")
        
        assert model is not None, "Model is None"
        assert label_map is not None, "Label map is None"
        assert feature_importance is not None, "Feature importance is None"
        assert len(label_map) == 3, f"Expected 3 labels, got {len(label_map)}"
        
        print("✅ Model artifacts loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def test_schemas():
    """Test Pydantic schemas."""
    print("\n🧪 Testing schemas...")
    try:
        from app.schemas import PatientInput, PredictionResponse
        
        # Test valid patient input
        patient = PatientInput(
            heart_rate=80,
            systolic_bp=120,
            diastolic_bp=80,
            oxygen_saturation=98,
            temperature=37.0,
            respiratory_rate=16,
            chest_pain=0,
            fever=0,
            breathing_difficulty=0,
            injury_type=0,
            diabetes=0,
            heart_disease=0,
            hypertension=0,
            asthma=0,
            age=35,
            gender="male"
        )
        
        print(f"   Patient created: age={patient.age}, HR={patient.heart_rate}")
        
        # Test prediction response
        response = PredictionResponse(
            severity="Minor",
            severity_code=2,
            confidence=0.95
        )
        
        print(f"   Response created: {response.severity} ({response.confidence})")
        
        print("✅ Schemas working correctly")
        return True
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

def test_utility_functions():
    """Test utility functions."""
    print("\n🧪 Testing utility functions...")
    try:
        from app.utils import severity_code_to_name, get_color
        
        # Test severity mapping
        assert severity_code_to_name(0) == "Immediate"
        assert severity_code_to_name(1) == "Urgent"
        assert severity_code_to_name(2) == "Moderate"
        assert severity_code_to_name(3) == "Minor"
        
        # Test color mapping
        assert get_color("Immediate") == "#ff4d4d"
        assert get_color("Urgent") == "#ff9500"
        assert get_color("Moderate") == "#ffd200"
        assert get_color("Minor") == "#4caf50"
        
        print("✅ Utility functions working correctly")
        return True
    except Exception as e:
        print(f"❌ Utility function test failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app configuration."""
    print("\n🧪 Testing FastAPI app...")
    try:
        from app.main import app
        
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")
        print(f"   Routes: {len(app.routes)}")
        
        # Check routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        expected_routes = ['/predict', '/feature_importance', '/explain', '/ping']
        
        for route in expected_routes:
            if route in routes:
                print(f"   ✓ Route {route} exists")
            else:
                print(f"   ✗ Route {route} missing")
                return False
        
        print("✅ FastAPI app configured correctly")
        return True
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False

def test_prediction_logic():
    """Test prediction logic without starting server."""
    print("\n🧪 Testing prediction logic...")
    try:
        from app.utils import load_artifacts
        import pandas as pd
        
        model, label_map, _ = load_artifacts()
        
        # Test patient data
        patient_data = {
            "heart_rate": 110,
            "systolic_bp": 115,
            "diastolic_bp": 75,
            "oxygen_saturation": 88,
            "temperature": 38.2,
            "respiratory_rate": 28,
            "chest_pain": 1,
            "fever": 1,
            "breathing_difficulty": 1,
            "injury_type": 0,
            "diabetes": 0,
            "heart_disease": 1,
            "hypertension": 0,
            "asthma": 0,
            "age": 68,
            "gender": "male"
        }
        
        df = pd.DataFrame([patient_data])
        probs = model.predict_proba(df)[0]
        pred_index = int(probs.argmax())
        pred_name = label_map[str(pred_index)]
        confidence = float(probs[pred_index])
        
        print(f"   Prediction: {pred_name} (code {pred_index})")
        print(f"   Confidence: {confidence:.4f}")
        print(f"   All probabilities: {[f'{p:.4f}' for p in probs]}")
        
        assert pred_name in ["Urgent", "Moderate", "Minor"], f"Invalid prediction: {pred_name}"
        assert 0 <= confidence <= 1, f"Invalid confidence: {confidence}"
        
        print("✅ Prediction logic working correctly")
        return True
    except Exception as e:
        print(f"❌ Prediction logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🔍 TRIAGE-X BACKEND VERIFICATION")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_logger,
        test_model_loading,
        test_schemas,
        test_utility_functions,
        test_fastapi_app,
        test_prediction_logic,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED - Backend is ready!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Check errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
