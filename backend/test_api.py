"""
Simple test script for the Triage-X API.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_ping():
    """Test ping endpoint."""
    print("🔍 Testing /ping endpoint...")
    response = requests.get(f"{BASE_URL}/ping")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

def test_predict():
    """Test prediction endpoint."""
    print("🔍 Testing /predict endpoint...")
    
    # Test patient data
    patient_data = {
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
    
    response = requests.post(f"{BASE_URL}/predict", json=patient_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Severity: {result['severity']}")
        print(f"   Confidence: {result['confidence']:.4f}")
        print(f"   Severity Code: {result['severity_code']}")
    else:
        print(f"   Error: {response.text}")
    print()

def test_feature_importance():
    """Test feature importance endpoint."""
    print("🔍 Testing /feature_importance endpoint...")
    response = requests.get(f"{BASE_URL}/feature_importance")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        importance = data['importance']
        print(f"   Top 5 features:")
        for feature, score in importance[:5]:
            print(f"     - {feature}: {score:.2f}")
    else:
        print(f"   Error: {response.text}")
    print()

if __name__ == "__main__":
    print("🧪 Testing Triage-X API\n")
    print("=" * 60)
    
    try:
        test_ping()
        test_predict()
        test_feature_importance()
        
        print("=" * 60)
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running:")
        print("   cd backend && python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Test failed: {e}")
