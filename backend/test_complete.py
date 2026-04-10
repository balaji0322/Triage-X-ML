"""
Complete backend test - verifies all components work together.
"""
import json
import pandas as pd
from app.main import app
from app.utils import load_artifacts, get_color, severity_code_to_name
from app.schemas import PatientInput, PredictionResponse
from fastapi.testclient import TestClient

print("🧪 Complete Backend Test\n")
print("=" * 60)

# Test 1: Load artifacts
print("\n1️⃣  Testing artifact loading...")
try:
    model, label_map, feature_imp = load_artifacts()
    print(f"   ✅ Model loaded: {type(model).__name__}")
    print(f"   ✅ Label map: {label_map}")
    print(f"   ✅ Feature importance: {len(feature_imp)} features")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Test 2: Utility functions
print("\n2️⃣  Testing utility functions...")
try:
    for code in range(3):
        name = severity_code_to_name(code)
        color = get_color(name)
        print(f"   Code {code} → {name} → {color}")
    print("   ✅ Utility functions working")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Test 3: Direct prediction
print("\n3️⃣  Testing direct prediction...")
try:
    test_patient = {
        "heart_rate": 110,
        "systolic_bp": 85,
        "diastolic_bp": 60,
        "oxygen_saturation": 88,
        "temperature": 39.2,
        "respiratory_rate": 28,
        "age": 75,
        "gender": "male",
        "chest_pain": 1,
        "fever": 1,
        "breathing_difficulty": 1,
        "injury_type": 0,
        "diabetes": 1,
        "heart_disease": 1,
        "hypertension": 1,
        "asthma": 0
    }
    
    df = pd.DataFrame([test_patient])
    probs = model.predict_proba(df)[0]
    pred_index = int(probs.argmax())
    pred_name = label_map[str(pred_index)]
    confidence = float(probs[pred_index])
    
    print(f"   Prediction: {pred_name}")
    print(f"   Confidence: {confidence:.4f}")
    print(f"   Code: {pred_index}")
    print("   ✅ Direct prediction working")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Test 4: Pydantic validation
print("\n4️⃣  Testing Pydantic schema validation...")
try:
    patient_input = PatientInput(**test_patient)
    print(f"   ✅ PatientInput validated: {patient_input.age} years old, {patient_input.gender}")
    
    response = PredictionResponse(
        severity=pred_name,
        severity_code=pred_index,
        confidence=confidence
    )
    print(f"   ✅ PredictionResponse created: {response.severity}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Test 5: FastAPI endpoints
print("\n5️⃣  Testing FastAPI endpoints...")
try:
    client = TestClient(app)
    
    # Test ping
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json()["msg"] == "pong"
    print("   ✅ /ping endpoint working")
    
    # Test predict
    response = client.post("/predict", json=test_patient)
    assert response.status_code == 200
    result = response.json()
    assert "severity" in result
    assert "confidence" in result
    assert "severity_code" in result
    print(f"   ✅ /predict endpoint working: {result['severity']} ({result['confidence']:.4f})")
    
    # Test feature importance
    response = client.get("/feature_importance")
    assert response.status_code == 200
    data = response.json()
    assert "importance" in data
    print(f"   ✅ /feature_importance endpoint working: {len(data['importance'])} features")
    
except Exception as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED! Backend is ready for production.")
print("\nTo start the server:")
print("  python run_server.py")
print("  or")
print("  uvicorn app.main:app --reload")
