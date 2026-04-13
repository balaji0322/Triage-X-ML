# ⚡ GPS Tracking - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Seed Hospital Data (One-Time)
```bash
cd backend
python seed_hospital_data.py
```

**Expected Output**:
```
✅ Created: 13 hospitals
✅ Total: 14 hospitals with GPS data
```

### Step 2: Start Backend
```bash
cd backend
python run_server.py
```

**Expected Output**:
```
✅ Database connected
✅ Model artifacts loaded
🚀 TRIAGE‑X service ready
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Start Frontend
```bash
cd frontend
npm start
```

**Expected Output**:
```
Compiled successfully!
Local: http://localhost:3000
```

---

## 🧪 Test the System

### Run GPS Tests
```bash
cd backend
python test_gps_tracking.py
```

**Expected Output**:
```
✅ PASS - Haversine Distance
✅ PASS - Hospital Scoring
✅ PASS - Hospital Database
✅ PASS - Nearest Hospitals
🎉 ALL TESTS PASSED - GPS TRACKING READY!
```

---

## 🚑 Use Ambulance Dashboard

1. **Open**: http://localhost:3000
2. **Login** as ambulance
3. **Allow GPS** when browser prompts
4. **See Map** with:
   - 🚑 Your location (red)
   - 🏥 Nearby hospitals (blue)
   - ⭐ Recommended hospital (green)
5. **Location updates** every 5 seconds automatically

---

## 🏥 Use Hospital Dashboard

1. **Open**: http://localhost:3000
2. **Login** as hospital
3. **See Map** with:
   - 🏥 Your hospital (blue)
   - 🚑 Active ambulances (red)
   - Movement trails (dotted lines)
4. **Active Panel** shows:
   - Ambulance numbers
   - Driver names
   - Current speeds
   - Last update times

---

## 📍 Features Available

### Ambulance Features
✅ Real-time GPS tracking  
✅ Nearby hospitals on map  
✅ AI-recommended hospital  
✅ Distance to each hospital  
✅ Hospital bed availability  
✅ Interactive map popups  

### Hospital Features
✅ Track multiple ambulances  
✅ See movement trails  
✅ Real-time position updates  
✅ Ambulance speed indicators  
✅ Active ambulances list  
✅ Toggle map/table view  

---

## 🔧 Troubleshooting

### "Unable to get your location"
**Fix**: Enable location in browser settings

### "No hospitals on map"
**Fix**: Run `python seed_hospital_data.py`

### "WebSocket disconnected"
**Fix**: Auto-reconnects in 3 seconds (5 attempts)

### "Map not loading"
**Fix**: Clear browser cache and reload

---

## 📊 System Status

Check system health:
```bash
curl http://localhost:8000/ping
```

Expected: `{"msg":"pong","status":"healthy"}`

---

## 🎯 Quick Commands

```bash
# Seed hospitals
cd backend && python seed_hospital_data.py

# Run tests
cd backend && python test_gps_tracking.py

# Start backend
cd backend && python run_server.py

# Start frontend
cd frontend && npm start

# Check health
curl http://localhost:8000/ping
```

---

## ✅ Success Indicators

### Backend Running
- ✅ "TRIAGE‑X service ready"
- ✅ "Uvicorn running on http://0.0.0.0:8000"

### Frontend Running
- ✅ "Compiled successfully!"
- ✅ "Local: http://localhost:3000"

### GPS Working
- ✅ Green "🟢 GPS Active" indicator
- ✅ Map shows your location
- ✅ Hospitals visible on map

### WebSocket Connected
- ✅ Browser console: "✅ Location WebSocket connected"
- ✅ No errors in console

---

## 📱 Mobile Testing

1. **Get local IP**: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. **Open on mobile**: `http://YOUR_IP:3000`
3. **Allow GPS** on mobile browser
4. **Test tracking** while moving

---

## 🎉 You're Ready!

The GPS tracking system is now operational. Ambulances can see nearby hospitals with AI recommendations, and hospitals can track ambulances in real-time.

**System Status**: 🟢 OPERATIONAL

---

**Quick Start Version**: 1.0  
**Last Updated**: April 13, 2026
