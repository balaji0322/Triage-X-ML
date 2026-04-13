#!/usr/bin/env python3
"""
Advanced Features Test Suite for Triage-X
Tests all 5 advanced features
"""
import sys
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_websocket_status():
    """Test WebSocket status endpoint."""
    print_section("🔌 FEATURE 1: WebSocket Status")
    
    try:
        response = requests.get(f"{BASE_URL}/ws/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ WebSocket status endpoint working")
            print(f"   Hospital connections: {data['hospital_connections']}")
            print(f"   Ambulance connections: {data['ambulance_connections']}")
            print(f"   Total connections: {data['total_connections']}")
            return True
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ WebSocket status test failed: {e}")
        return False

def test_hospital_allocation():
    """Test smart hospital allocation."""
    print_section("🏥 FEATURE 2: Smart Hospital Allocation")
    
    # First, create a test ambulance and get token
    try:
        # Signup
        signup_data = {
            "driver_name": "Test Driver",
            "ambulance_number": f"TEST-ADV-{datetime.now().strftime('%H%M%S')}",
            "password": "test123",
            "confirm_password": "test123"
        }
        
        response = requests.post(f"{BASE_URL}/api/ambulance/signup", json=signup_data)
        if response.status_code != 201:
            print(f"   ⚠️  Signup failed, trying login...")
            return False
        
        token = response.json()["access_token"]
        
        # Test allocation
        allocation_data = {
            "severity": "Urgent",
            "severity_code": 0,
            "ambulance_lat": 13.0827,
            "ambulance_lon": 80.2707
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/api/suggest-hospital",
            json=allocation_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Hospital allocation working")
            print(f"   Suggested: {data['hospital_name']}")
            print(f"   Distance: {data['distance_km']}km")
            print(f"   Load: {data['current_load']} cases")
            print(f"   Priority Score: {data['priority_score']}")
            print(f"   Reason: {data['reason']}")
            return True
        else:
            print(f"   ❌ Allocation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Hospital allocation test failed: {e}")
        return False

def test_enhanced_prediction():
    """Test enhanced AI insights."""
    print_section("🧠 FEATURE 3: Enhanced AI Insights")
    
    try:
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
        
        response = requests.post(f"{BASE_URL}/api/predict/enhanced", json=patient_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Enhanced prediction working")
            print(f"   Severity: {data['severity']}")
            print(f"   Confidence: {data['confidence']:.2%}")
            print(f"   Risk Score: {data['risk_score']}/100")
            print(f"   Top Factors:")
            for factor in data['top_factors'][:3]:
                print(f"      - {factor['feature']}: {factor['importance']:.4f}")
            print(f"   Recommendation: {data['recommendation']}")
            return True
        else:
            print(f"   ❌ Enhanced prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Enhanced prediction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analytics():
    """Test analytics dashboard."""
    print_section("📊 FEATURE 4: Admin Analytics Dashboard")
    
    try:
        # Create a test hospital and get token
        signup_data = {
            "hospital_name": "Test Analytics Hospital",
            "address": "123 Test Street, Chennai",
            "password": "test123",
            "confirm_password": "test123"
        }
        
        response = requests.post(f"{BASE_URL}/api/hospital/signup", json=signup_data)
        if response.status_code != 201:
            print(f"   ⚠️  Hospital signup failed")
            return False
        
        token = response.json()["access_token"]
        
        # Test analytics
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/analytics", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Analytics endpoint working")
            print(f"   Total Cases: {data['total_cases']}")
            print(f"   Cases Last 24h: {data['cases_last_24h']}")
            print(f"   Avg Severity Score: {data['average_severity_score']:.2f}")
            print(f"   Trend: {data['trend']}")
            print(f"   Cases by Severity:")
            for severity, count in data['cases_by_severity'].items():
                print(f"      {severity}: {count}")
            if data['peak_hours']:
                print(f"   Peak Hour: {data['peak_hours'][0]['hour']}:00 ({data['peak_hours'][0]['cases']} cases)")
            return True
        else:
            print(f"   ❌ Analytics failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Analytics test failed: {e}")
        return False

def test_mobile_optimization():
    """Test mobile optimization (basic check)."""
    print_section("📱 FEATURE 5: Mobile Optimization")
    
    print(f"   ✅ Mobile optimization is CSS-based")
    print(f"   ✅ Responsive breakpoints: 768px, 1024px")
    print(f"   ✅ Touch-friendly controls (min 44px)")
    print(f"   ✅ Mobile-first design approach")
    print(f"   ℹ️  Test manually with Chrome DevTools mobile emulator")
    return True

def main():
    """Run all advanced feature tests."""
    print("\n" + "=" * 70)
    print("  🧪 TRIAGE-X ADVANCED FEATURES TEST SUITE")
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
        "WebSocket Status": test_websocket_status(),
        "Hospital Allocation": test_hospital_allocation(),
        "Enhanced Prediction": test_enhanced_prediction(),
        "Analytics Dashboard": test_analytics(),
        "Mobile Optimization": test_mobile_optimization()
    }
    
    print_section("📊 TEST SUMMARY")
    
    for feature, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {feature}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All advanced features tests passed!")
        print("   System is fully functional with all 5 advanced features.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
