#!/usr/bin/env python3
"""
Integration Test for Triage-X System
Tests the complete flow: Auth → Prediction → Case Management
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_ambulance_flow():
    """Test complete ambulance user flow."""
    print_section("🚑 AMBULANCE FLOW TEST")
    
    # 1. Signup
    print("\n1️⃣  Testing Ambulance Signup...")
    signup_data = {
        "driver_name": "Test Driver",
        "ambulance_number": f"TEST-{datetime.now().strftime('%H%M%S')}",
        "password": "test123",
        "confirm_password": "test123"
    }
    
    response = requests.post(f"{BASE_URL}/api/ambulance/signup", json=signup_data)
    if response.status_code == 201:
        print(f"   ✅ Signup successful")
        signup_result = response.json()
        token = signup_result["access_token"]
        ambulance_number = signup_result["user_data"]["ambulance_number"]
        print(f"   Token: {token[:20]}...")
        print(f"   Ambulance: {ambulance_number}")
    else:
        print(f"   ❌ Signup failed: {response.text}")
        return False
    
    # 2. Login
    print("\n2️⃣  Testing Ambulance Login...")
    login_data = {
        "ambulance_number": ambulance_number,
        "password": "test123"
    }
    
    response = requests.post(f"{BASE_URL}/api/ambulance/login", json=login_data)
    if response.status_code == 200:
        print(f"   ✅ Login successful")
        token = response.json()["access_token"]
    else:
        print(f"   ❌ Login failed: {response.text}")
        return False
    
    # 3. Predict
    print("\n3️⃣  Testing ML Prediction...")
    patient_data = {
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
    
    response = requests.post(f"{BASE_URL}/predict", json=patient_data)
    if response.status_code == 200:
        prediction = response.json()
        print(f"   ✅ Prediction successful")
        print(f"   Severity: {prediction['severity']}")
        print(f"   Confidence: {prediction['confidence']:.2%}")
        print(f"   Code: {prediction['severity_code']}")
    else:
        print(f"   ❌ Prediction failed: {response.text}")
        return False
    
    # 4. Send Case
    print("\n4️⃣  Testing Case Submission...")
    case_data = {
        "patient_data": patient_data,
        "severity": prediction["severity"],
        "confidence": prediction["confidence"]
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/send-case", json=case_data, headers=headers)
    if response.status_code == 200:
        case = response.json()
        print(f"   ✅ Case submitted successfully")
        print(f"   Case ID: {case['case_id']}")
        print(f"   Severity: {case['severity']}")
    else:
        print(f"   ❌ Case submission failed: {response.text}")
        return False
    
    # 5. Get Recent Cases
    print("\n5️⃣  Testing Recent Cases Retrieval...")
    response = requests.get(f"{BASE_URL}/api/ambulance/recent-cases", headers=headers)
    if response.status_code == 200:
        cases = response.json()
        print(f"   ✅ Retrieved {len(cases)} recent cases")
        if cases:
            print(f"   Latest case: {cases[0]['severity']} - {cases[0]['timestamp']}")
    else:
        print(f"   ❌ Recent cases retrieval failed: {response.text}")
        return False
    
    return True

def test_hospital_flow():
    """Test complete hospital user flow."""
    print_section("🏥 HOSPITAL FLOW TEST")
    
    # 1. Signup
    print("\n1️⃣  Testing Hospital Signup...")
    signup_data = {
        "hospital_name": "Test Hospital",
        "address": "123 Test Street, New York",
        "password": "hospital123",
        "confirm_password": "hospital123"
    }
    
    response = requests.post(f"{BASE_URL}/api/hospital/signup", json=signup_data)
    if response.status_code == 201:
        print(f"   ✅ Signup successful")
        signup_result = response.json()
        token = signup_result["access_token"]
        hospital_id = signup_result["user_data"]["hospital_id"]
        print(f"   Token: {token[:20]}...")
        print(f"   Hospital ID: {hospital_id}")
    else:
        print(f"   ❌ Signup failed: {response.text}")
        return False
    
    # 2. Login
    print("\n2️⃣  Testing Hospital Login...")
    login_data = {
        "hospital_id": hospital_id,
        "password": "hospital123"
    }
    
    response = requests.post(f"{BASE_URL}/api/hospital/login", json=login_data)
    if response.status_code == 200:
        print(f"   ✅ Login successful")
        token = response.json()["access_token"]
    else:
        print(f"   ❌ Login failed: {response.text}")
        return False
    
    # 3. Get All Cases
    print("\n3️⃣  Testing Cases Retrieval...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/cases", headers=headers)
    if response.status_code == 200:
        cases = response.json()
        print(f"   ✅ Retrieved {len(cases)} total cases")
        if cases:
            severity_counts = {}
            for case in cases:
                severity = case['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            print(f"   Breakdown: {severity_counts}")
    else:
        print(f"   ❌ Cases retrieval failed: {response.text}")
        return False
    
    # 4. Get Statistics
    print("\n4️⃣  Testing Statistics Retrieval...")
    response = requests.get(f"{BASE_URL}/api/hospital/stats", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Statistics retrieved")
        print(f"   Immediate: {stats.get('Immediate', 0)}")
        print(f"   Urgent: {stats.get('Urgent', 0)}")
        print(f"   Moderate: {stats.get('Moderate', 0)}")
        print(f"   Minor: {stats.get('Minor', 0)}")
        print(f"   Total: {stats.get('total', 0)}")
    else:
        print(f"   ❌ Statistics retrieval failed: {response.text}")
        return False
    
    return True

def test_public_endpoints():
    """Test public endpoints."""
    print_section("🌐 PUBLIC ENDPOINTS TEST")
    
    # 1. Health Check
    print("\n1️⃣  Testing Health Check...")
    response = requests.get(f"{BASE_URL}/ping")
    if response.status_code == 200:
        print(f"   ✅ Health check passed: {response.json()}")
    else:
        print(f"   ❌ Health check failed")
        return False
    
    # 2. Feature Importance
    print("\n2️⃣  Testing Feature Importance...")
    response = requests.get(f"{BASE_URL}/feature_importance")
    if response.status_code == 200:
        data = response.json()
        importance = data.get("importance", [])
        print(f"   ✅ Feature importance retrieved: {len(importance)} features")
        if importance:
            print(f"   Top feature: {importance[0][0]} = {importance[0][1]:.4f}")
    else:
        print(f"   ❌ Feature importance failed")
        return False
    
    return True

def main():
    """Run all integration tests."""
    print("\n" + "=" * 70)
    print("  🧪 TRIAGE-X INTEGRATION TEST SUITE")
    print("=" * 70)
    print(f"\n  Testing against: {BASE_URL}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/ping", timeout=2)
        if response.status_code != 200:
            print("\n❌ Server is not responding correctly!")
            print("   Please start the server with: python backend/run_server.py")
            return 1
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("   Please start the server with: python backend/run_server.py")
        return 1
    
    results = {
        "Public Endpoints": test_public_endpoints(),
        "Ambulance Flow": test_ambulance_flow(),
        "Hospital Flow": test_hospital_flow()
    }
    
    print_section("📊 TEST SUMMARY")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All integration tests passed!")
        print("   System is fully functional and ready for use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
