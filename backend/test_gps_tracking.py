#!/usr/bin/env python3
"""
Test GPS Tracking System
Verifies location tracking and hospital recommendation
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.location_tracking import haversine_distance, calculate_hospital_score
from app.database import connect_db, get_db
from loguru import logger as log

def test_haversine_distance():
    """Test distance calculation."""
    log.info("🧪 Testing Haversine distance calculation...")
    
    # Chennai to Bangalore
    chennai = (13.0827, 80.2707)
    bangalore = (12.9716, 77.5946)
    
    distance = haversine_distance(chennai[0], chennai[1], bangalore[0], bangalore[1])
    
    # Expected: ~290 km
    assert 280 < distance < 300, f"Distance calculation error: {distance} km"
    
    log.success(f"✅ Distance calculation correct: {distance} km")
    return True


def test_hospital_scoring():
    """Test hospital scoring algorithm."""
    log.info("🧪 Testing hospital scoring...")
    
    # Test case 1: Close hospital with many beds
    score1 = calculate_hospital_score(distance_km=5, available_beds=50, current_load=10)
    
    # Test case 2: Far hospital with many beds
    score2 = calculate_hospital_score(distance_km=20, available_beds=50, current_load=10)
    
    # Test case 3: Close hospital with few beds
    score3 = calculate_hospital_score(distance_km=5, available_beds=10, current_load=10)
    
    # Score 1 should be best (lowest)
    assert score1 < score2, "Distance weight not working"
    assert score1 < score3, "Bed weight not working"
    
    log.success(f"✅ Scoring algorithm correct")
    log.info(f"   - Close + many beds: {score1}")
    log.info(f"   - Far + many beds: {score2}")
    log.info(f"   - Close + few beds: {score3}")
    
    return True


def test_hospital_data():
    """Test hospital database has GPS data."""
    log.info("🧪 Testing hospital database...")
    
    connect_db()
    db = get_db()
    
    # Count hospitals with GPS data
    hospitals_with_gps = db.hospitals.count_documents({
        "latitude": {"$exists": True},
        "longitude": {"$exists": True}
    })
    
    assert hospitals_with_gps > 0, "No hospitals with GPS data found"
    
    # Get sample hospital
    sample = db.hospitals.find_one({
        "latitude": {"$exists": True}
    })
    
    assert "available_beds" in sample, "Hospital missing available_beds"
    assert "current_load" in sample, "Hospital missing current_load"
    
    log.success(f"✅ Hospital database correct")
    log.info(f"   - Hospitals with GPS: {hospitals_with_gps}")
    log.info(f"   - Sample: {sample['hospital_name']}")
    log.info(f"   - Location: ({sample['latitude']}, {sample['longitude']})")
    log.info(f"   - Beds: {sample['available_beds']}, Load: {sample['current_load']}")
    
    return True


def test_nearest_hospitals():
    """Test nearest hospitals API logic."""
    log.info("🧪 Testing nearest hospitals logic...")
    
    connect_db()
    db = get_db()
    
    # Test location (Chennai)
    test_lat = 13.0827
    test_lng = 80.2707
    
    # Get all hospitals
    hospitals = list(db.hospitals.find({
        "latitude": {"$exists": True},
        "longitude": {"$exists": True}
    }))
    
    assert len(hospitals) > 0, "No hospitals found"
    
    # Calculate scores
    hospital_scores = []
    for hospital in hospitals:
        distance = haversine_distance(
            test_lat, test_lng,
            hospital["latitude"],
            hospital["longitude"]
        )
        
        score = calculate_hospital_score(
            distance,
            hospital.get("available_beds", 10),
            hospital.get("current_load", 0)
        )
        
        hospital_scores.append({
            "name": hospital["hospital_name"],
            "distance": distance,
            "score": score
        })
    
    # Sort by score
    hospital_scores.sort(key=lambda x: x["score"])
    
    recommended = hospital_scores[0]
    
    log.success(f"✅ Nearest hospitals logic correct")
    log.info(f"   - Total hospitals: {len(hospitals)}")
    log.info(f"   - Recommended: {recommended['name']}")
    log.info(f"   - Distance: {recommended['distance']} km")
    log.info(f"   - Score: {recommended['score']}")
    
    return True


def main():
    """Run all tests."""
    log.info("=" * 60)
    log.info("🧪 GPS TRACKING SYSTEM TESTS")
    log.info("=" * 60)
    
    tests = [
        ("Haversine Distance", test_haversine_distance),
        ("Hospital Scoring", test_hospital_scoring),
        ("Hospital Database", test_hospital_data),
        ("Nearest Hospitals", test_nearest_hospitals),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
            log.info("")
        except Exception as e:
            log.error(f"❌ {name} test failed: {e}")
            results[name] = False
            log.info("")
    
    # Summary
    log.info("=" * 60)
    log.info("📊 TEST SUMMARY")
    log.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        log.info(f"{status} - {name}")
    
    log.info("=" * 60)
    log.info(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        log.success("🎉 ALL TESTS PASSED - GPS TRACKING READY!")
        return 0
    else:
        log.error("⚠️  SOME TESTS FAILED - REVIEW REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
