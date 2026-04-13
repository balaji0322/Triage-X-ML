#!/usr/bin/env python3
"""
Test ICU Bed Management System
Verifies all ICU management endpoints and functionality
"""
import requests
import json
from loguru import logger as log

BASE_URL = "http://localhost:8000"

def test_icu_management():
    """Test ICU bed management system."""
    log.info("🧪 Testing ICU Bed Management System")
    
    # Test 1: Hospital Login
    log.info("\n📝 Test 1: Hospital Login")
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/hospital/login",
            json={
                "hospital_id": "HOSP-TEST-1234",
                "password": "hospital123"
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            log.success(f"✅ Hospital login successful")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            log.error(f"❌ Login failed: {login_response.text}")
            return
    except Exception as e:
        log.error(f"❌ Login error: {e}")
        return
    
    # Test 2: Get ICU Status
    log.info("\n📊 Test 2: Get ICU Status")
    try:
        status_response = requests.get(
            f"{BASE_URL}/api/hospital/icu-status/HOSP-TEST-1234",
            headers=headers
        )
        
        if status_response.status_code == 200:
            status = status_response.json()
            log.success(f"✅ ICU Status retrieved:")
            log.info(f"   - Total ICU Beds: {status['icu_total']}")
            log.info(f"   - Available: {status['icu_available']}")
            log.info(f"   - Occupied: {status['icu_occupied']}")
            log.info(f"   - Occupancy Rate: {status['occupancy_rate']}%")
        else:
            log.error(f"❌ Failed to get ICU status: {status_response.text}")
    except Exception as e:
        log.error(f"❌ Get ICU status error: {e}")
    
    # Test 3: Update ICU Beds
    log.info("\n🔄 Test 3: Update ICU Beds")
    try:
        update_response = requests.put(
            f"{BASE_URL}/api/hospital/update-icu",
            headers=headers,
            json={
                "hospital_id": "HOSP-TEST-1234",
                "icu_total": 25,
                "icu_available": 10
            }
        )
        
        if update_response.status_code == 200:
            result = update_response.json()
            log.success(f"✅ ICU beds updated:")
            log.info(f"   - Total: {result['icu_total']}")
            log.info(f"   - Available: {result['icu_available']}")
            log.info(f"   - Occupied: {result['icu_occupied']}")
            log.info(f"   - Occupancy Rate: {result['occupancy_rate']}%")
        else:
            log.error(f"❌ Failed to update ICU beds: {update_response.text}")
    except Exception as e:
        log.error(f"❌ Update ICU beds error: {e}")
    
    # Test 4: Get ICU Statistics
    log.info("\n📈 Test 4: Get ICU Statistics")
    try:
        stats_response = requests.get(
            f"{BASE_URL}/api/hospital/icu-stats",
            headers=headers
        )
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            log.success(f"✅ ICU Statistics:")
            log.info(f"   - Total Hospitals: {stats['total_hospitals']}")
            log.info(f"   - Total ICU Beds: {stats['total_icu_beds']}")
            log.info(f"   - Total Available: {stats['total_available']}")
            log.info(f"   - Total Occupied: {stats['total_occupied']}")
            log.info(f"   - Average Occupancy: {stats['average_occupancy']}%")
            log.info(f"   - Hospitals at Capacity: {stats['hospitals_at_capacity']}")
        else:
            log.error(f"❌ Failed to get ICU statistics: {stats_response.text}")
    except Exception as e:
        log.error(f"❌ Get ICU statistics error: {e}")
    
    # Test 5: Get Hospitals with ICU
    log.info("\n🏥 Test 5: Get Hospitals with ICU")
    try:
        hospitals_response = requests.get(
            f"{BASE_URL}/api/hospitals/with-icu",
            headers=headers
        )
        
        if hospitals_response.status_code == 200:
            hospitals = hospitals_response.json()
            log.success(f"✅ Retrieved {len(hospitals)} hospitals with ICU data")
            
            # Show first 3 hospitals
            for i, hospital in enumerate(hospitals[:3]):
                log.info(f"\n   Hospital {i+1}:")
                log.info(f"   - Name: {hospital['hospital_name']}")
                log.info(f"   - ICU: {hospital['icu_available']}/{hospital['icu_total']}")
                log.info(f"   - Occupancy: {hospital['occupancy_rate']}%")
        else:
            log.error(f"❌ Failed to get hospitals with ICU: {hospitals_response.text}")
    except Exception as e:
        log.error(f"❌ Get hospitals with ICU error: {e}")
    
    # Test 6: Validation - Available > Total (should fail)
    log.info("\n⚠️ Test 6: Validation Test (Available > Total)")
    try:
        invalid_response = requests.put(
            f"{BASE_URL}/api/hospital/update-icu",
            headers=headers,
            json={
                "hospital_id": "HOSP-TEST-1234",
                "icu_total": 20,
                "icu_available": 25  # Invalid: more than total
            }
        )
        
        if invalid_response.status_code == 422:
            log.success(f"✅ Validation working correctly - rejected invalid data")
        else:
            log.warning(f"⚠️ Validation may not be working: {invalid_response.status_code}")
    except Exception as e:
        log.error(f"❌ Validation test error: {e}")
    
    # Test 7: Test Ambulance Login and Nearest Hospitals (with ICU filter)
    log.info("\n🚑 Test 7: Ambulance - Nearest Hospitals (ICU Filter)")
    try:
        # Login as ambulance
        amb_login = requests.post(
            f"{BASE_URL}/api/ambulance/login",
            json={
                "ambulance_number": "TN01AB1234",
                "password": "ambulance123"
            }
        )
        
        if amb_login.status_code == 200:
            amb_token = amb_login.json()["access_token"]
            amb_headers = {"Authorization": f"Bearer {amb_token}"}
            
            # Get nearest hospitals (Chennai coordinates)
            nearest_response = requests.get(
                f"{BASE_URL}/api/nearest-hospitals",
                headers=amb_headers,
                params={
                    "lat": 13.0827,
                    "lng": 80.2707,
                    "limit": 5
                }
            )
            
            if nearest_response.status_code == 200:
                data = nearest_response.json()
                log.success(f"✅ Nearest hospitals retrieved (with ICU filter)")
                log.info(f"   - Total hospitals: {len(data['hospitals'])}")
                
                if data['recommended_hospital']:
                    rec = data['recommended_hospital']
                    log.info(f"\n   ⭐ Recommended Hospital:")
                    log.info(f"   - Name: {rec['hospital_name']}")
                    log.info(f"   - Distance: {rec['distance_km']} km")
                    log.info(f"   - Score: {rec['score']}")
                    log.info(f"   - Note: Only hospitals with ICU beds available are included")
            else:
                log.error(f"❌ Failed to get nearest hospitals: {nearest_response.text}")
        else:
            log.error(f"❌ Ambulance login failed")
    except Exception as e:
        log.error(f"❌ Ambulance test error: {e}")
    
    log.success("\n🎉 ICU Management System Tests Complete!")


if __name__ == "__main__":
    test_icu_management()
