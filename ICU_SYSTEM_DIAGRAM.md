# ICU Bed Management System - Visual Architecture

## 🏗️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TRIAGE-X ICU MANAGEMENT SYSTEM                   │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐                              ┌──────────────────────┐
│  HOSPITAL DASHBOARD  │                              │ AMBULANCE DASHBOARD  │
│                      │                              │                      │
│  ┌────────────────┐  │                              │  ┌────────────────┐  │
│  │ ICU Status     │  │                              │  │ Real-Time Map  │  │
│  │ - Total: 25    │  │                              │  │                │  │
│  │ - Available: 10│  │                              │  │ 🚑 Ambulance   │  │
│  │ - Occupied: 15 │  │                              │  │                │  │
│  │ - Rate: 60%    │  │                              │  │ 🏥 Hospitals   │  │
│  └────────────────┘  │                              │  │ (with ICU)     │  │
│                      │                              │  └────────────────┘  │
│  ┌────────────────┐  │                              │                      │
│  │ Update Form    │  │                              │  ┌────────────────┐  │
│  │ Total: [___]   │  │                              │  │ Recommended    │  │
│  │ Available:[__] │  │                              │  │ Hospital       │  │
│  │ [Update ICU]   │  │                              │  │ ICU: 10/25     │  │
│  └────────────────┘  │                              │  └────────────────┘  │
└──────────┬───────────┘                              └──────────┬───────────┘
           │                                                     │
           │ PUT /api/hospital/update-icu                       │ GET /api/nearest-hospitals
           │                                                     │
           ▼                                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND                                │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    ICU MANAGEMENT MODULE                          │  │
│  │                                                                    │  │
│  │  PUT  /api/hospital/update-icu        ← Update ICU beds          │  │
│  │  GET  /api/hospital/icu-status/:id    ← Get ICU status           │  │
│  │  GET  /api/hospital/icu-stats         ← Get overall statistics   │  │
│  │  GET  /api/hospitals/with-icu         ← Get all hospitals        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                  LOCATION TRACKING MODULE                         │  │
│  │                                                                    │  │
│  │  GET /api/nearest-hospitals                                       │  │
│  │  ├─ Filter: icu_available > 0                                     │  │
│  │  ├─ Calculate: score = (0.5*dist) + (0.3*load) - (0.7*icu)       │  │
│  │  └─ Return: Sorted hospitals (lower score = better)              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    WEBSOCKET MANAGER                              │  │
│  │                                                                    │  │
│  │  broadcast_to_all() ─────────────────────────────────────────┐   │  │
│  │    │                                                          │   │  │
│  │    ├─► Hospital Connections (WebSocket)                      │   │  │
│  │    └─► Ambulance Connections (WebSocket)                     │   │  │
│  │                                                               │   │  │
│  │  Message: { type: "icu_update", hospital_id, icu_data }      │   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────┬────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            MONGODB DATABASE                              │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  hospitals Collection                                             │  │
│  │  {                                                                │  │
│  │    hospital_id: "HOSP-CHE-2694",                                  │  │
│  │    hospital_name: "Apollo Hospital",                              │  │
│  │    latitude: 13.0358,                                             │  │
│  │    longitude: 80.2464,                                            │  │
│  │    available_beds: 50,                                            │  │
│  │    current_load: 15,                                              │  │
│  │    icu_total: 20,           ← NEW                                │  │
│  │    icu_available: 8,        ← NEW                                │  │
│  │    icu_occupied: 12,        ← NEW (auto-calculated)              │  │
│  │    occupancy_rate: 60.0,    ← NEW (auto-calculated)              │  │
│  │    last_updated: ISODate()                                        │  │
│  │  }                                                                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Real-Time Update Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ICU UPDATE WORKFLOW                                 │
└─────────────────────────────────────────────────────────────────────────┘

STEP 1: Hospital Updates ICU Beds
┌──────────────────┐
│ Hospital Staff   │
│ Updates Form:    │
│ Total: 25        │
│ Available: 10    │
│ [Submit]         │
└────────┬─────────┘
         │
         ▼
STEP 2: API Request
┌──────────────────────────────────────┐
│ PUT /api/hospital/update-icu         │
│ {                                    │
│   hospital_id: "HOSP-TEST-1234",     │
│   icu_total: 25,                     │
│   icu_available: 10                  │
│ }                                    │
└────────┬─────────────────────────────┘
         │
         ▼
STEP 3: Backend Validation
┌──────────────────────────────────────┐
│ ✓ Validate: available ≤ total        │
│ ✓ Check: User owns this hospital     │
│ ✓ Calculate: occupied = total - avail│
│ ✓ Calculate: rate = (occupied/total) │
└────────┬─────────────────────────────┘
         │
         ▼
STEP 4: Database Update
┌──────────────────────────────────────┐
│ MongoDB Update:                      │
│ {                                    │
│   icu_total: 25,                     │
│   icu_available: 10,                 │
│   icu_occupied: 15,                  │
│   occupancy_rate: 60.0,              │
│   last_updated: NOW()                │
│ }                                    │
└────────┬─────────────────────────────┘
         │
         ▼
STEP 5: WebSocket Broadcast
┌──────────────────────────────────────┐
│ broadcast_to_all({                   │
│   type: "icu_update",                │
│   hospital_id: "HOSP-TEST-1234",     │
│   icu_total: 25,                     │
│   icu_available: 10,                 │
│   icu_occupied: 15,                  │
│   occupancy_rate: 60.0               │
│ })                                   │
└────────┬─────────────────────────────┘
         │
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Hospital        │ │ Hospital        │ │ Ambulance       │
│ Dashboard 1     │ │ Dashboard 2     │ │ Dashboard       │
│ (Real-time      │ │ (Real-time      │ │ (Map updates    │
│  update)        │ │  update)        │ │  instantly)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## 🚑 Smart Hospital Allocation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│              AMBULANCE HOSPITAL RECOMMENDATION FLOW                      │
└─────────────────────────────────────────────────────────────────────────┘

STEP 1: Ambulance Location
┌──────────────────┐
│ 🚑 Ambulance     │
│ Lat: 13.0827     │
│ Lng: 80.2707     │
└────────┬─────────┘
         │
         ▼
STEP 2: Request Nearest Hospitals
┌──────────────────────────────────────┐
│ GET /api/nearest-hospitals           │
│ ?lat=13.0827&lng=80.2707&limit=10    │
└────────┬─────────────────────────────┘
         │
         ▼
STEP 3: Filter Hospitals
┌──────────────────────────────────────┐
│ Query MongoDB:                       │
│ - latitude, longitude exists         │
│ - icu_available > 0  ← ICU FILTER    │
└────────┬─────────────────────────────┘
         │
         ▼
STEP 4: Calculate Scores
┌──────────────────────────────────────────────────────────────┐
│ For each hospital:                                           │
│                                                              │
│ Hospital A:                                                  │
│   Distance: 5.2 km                                           │
│   Current Load: 20                                           │
│   ICU Available: 8                                           │
│   Score = (0.5 × 5.2) + (0.3 × 20) - (0.7 × 8)             │
│   Score = 2.6 + 6.0 - 5.6 = 3.0                            │
│                                                              │
│ Hospital B:                                                  │
│   Distance: 3.8 km                                           │
│   Current Load: 25                                           │
│   ICU Available: 12                                          │
│   Score = (0.5 × 3.8) + (0.3 × 25) - (0.7 × 12)            │
│   Score = 1.9 + 7.5 - 8.4 = 1.0  ← BEST SCORE              │
│                                                              │
│ Hospital C:                                                  │
│   Distance: 2.5 km                                           │
│   Current Load: 30                                           │
│   ICU Available: 0  ← EXCLUDED (no ICU beds)                │
└──────────────────────────────────────────────────────────────┘
         │
         ▼
STEP 5: Sort & Return
┌──────────────────────────────────────┐
│ Sorted Hospitals (by score):        │
│ 1. Hospital B (Score: 1.0) ⭐        │
│ 2. Hospital A (Score: 3.0)           │
│ 3. Hospital D (Score: 4.2)           │
│                                      │
│ Recommended: Hospital B              │
└────────┬─────────────────────────────┘
         │
         ▼
STEP 6: Display on Map
┌──────────────────────────────────────┐
│ 🗺️ Ambulance Map                     │
│                                      │
│ 🚑 Your Location                     │
│                                      │
│ ⭐ Hospital B (Recommended)          │
│    Distance: 3.8 km                  │
│    ICU: 12/20 available              │
│    Score: 1.0                        │
│                                      │
│ 🏥 Hospital A                        │
│    Distance: 5.2 km                  │
│    ICU: 8/20 available               │
│                                      │
│ 🏥 Hospital D                        │
│    Distance: 7.1 km                  │
│    ICU: 5/15 available               │
└──────────────────────────────────────┘
```

---

## 📊 Data Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HOSPITAL DOCUMENT SCHEMA                         │
└─────────────────────────────────────────────────────────────────────────┘

{
  // Identification
  "_id": ObjectId("..."),
  "hospital_id": "HOSP-CHE-2694",
  "hospital_name": "Apollo Hospital",
  
  // Location
  "address": "Chennai, India",
  "latitude": 13.0358,
  "longitude": 80.2464,
  "city": "Chennai",
  
  // General Capacity
  "available_beds": 50,
  "current_load": 15,
  
  // ICU Capacity (NEW)
  "icu_total": 20,              ← Total ICU beds
  "icu_available": 8,           ← Available ICU beds
  "icu_occupied": 12,           ← Occupied (auto-calculated)
  "occupancy_rate": 60.0,       ← Percentage (auto-calculated)
  
  // Authentication
  "password_hash": "$2b$12$...",
  
  // Timestamps
  "created_at": ISODate("2026-04-13T10:00:00Z"),
  "last_updated": ISODate("2026-04-13T14:02:50Z")
}

┌─────────────────────────────────────────────────────────────────────────┐
│                         INDEXES                                          │
└─────────────────────────────────────────────────────────────────────────┘

1. hospital_id (unique)
2. latitude, longitude (compound index for geospatial queries)
3. icu_available (for filtering hospitals with available ICU beds)
```

---

## 🎯 Scoring Algorithm Explained

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    HOSPITAL SCORING FORMULA                              │
└─────────────────────────────────────────────────────────────────────────┘

Score = (0.5 × Distance) + (0.3 × Load) - (0.7 × ICU Available)

┌──────────────────┬──────────┬─────────────────────────────────────────┐
│ Factor           │ Weight   │ Explanation                             │
├──────────────────┼──────────┼─────────────────────────────────────────┤
│ Distance (km)    │ +0.5     │ Closer hospitals are better             │
│                  │          │ (positive weight increases score)       │
├──────────────────┼──────────┼─────────────────────────────────────────┤
│ Current Load     │ +0.3     │ Higher load = busier hospital           │
│                  │          │ (positive weight increases score)       │
├──────────────────┼──────────┼─────────────────────────────────────────┤
│ ICU Available    │ -0.7     │ More ICU beds = better hospital         │
│                  │          │ (negative weight decreases score)       │
│                  │          │ HIGHEST PRIORITY                        │
└──────────────────┴──────────┴─────────────────────────────────────────┘

LOWER SCORE = BETTER HOSPITAL

Example Calculation:
─────────────────────────────────────────────────────────────────────────
Hospital: Apollo Hospital
  Distance: 5.2 km
  Current Load: 20 patients
  ICU Available: 8 beds

Score = (0.5 × 5.2) + (0.3 × 20) - (0.7 × 8)
      = 2.6 + 6.0 - 5.6
      = 3.0

Hospital: Fortis Hospital
  Distance: 3.8 km
  Current Load: 25 patients
  ICU Available: 12 beds

Score = (0.5 × 3.8) + (0.3 × 25) - (0.7 × 12)
      = 1.9 + 7.5 - 8.4
      = 1.0  ← BETTER SCORE (recommended)

Why Fortis is recommended:
✓ Slightly closer (3.8 km vs 5.2 km)
✓ More ICU beds available (12 vs 8) ← MOST IMPORTANT
✗ Slightly higher load (25 vs 20) ← Less important

The high weight on ICU availability (-0.7) ensures that hospitals with
more ICU beds are strongly preferred, even if they're slightly farther
or busier.
```

---

## 🔐 Security & Permissions

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PERMISSION MATRIX                                │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┬──────────┬──────────┬──────────┐
│ Endpoint             │ Hospital │ Ambulance│ Public   │
├──────────────────────┼──────────┼──────────┼──────────┤
│ PUT /update-icu      │ ✅ Own   │ ❌       │ ❌       │
│                      │   Only   │          │          │
├──────────────────────┼──────────┼──────────┼──────────┤
│ GET /icu-status/:id  │ ✅       │ ✅       │ ❌       │
├──────────────────────┼──────────┼──────────┼──────────┤
│ GET /icu-stats       │ ✅       │ ✅       │ ❌       │
├──────────────────────┼──────────┼──────────┼──────────┤
│ GET /hospitals/icu   │ ✅       │ ✅       │ ❌       │
├──────────────────────┼──────────┼──────────┼──────────┤
│ GET /nearest-hosp    │ ❌       │ ✅       │ ❌       │
└──────────────────────┴──────────┴──────────┴──────────┘

Validation Rules:
─────────────────────────────────────────────────────────
1. icu_available ≤ icu_total
2. icu_available ≥ 0
3. icu_total ≥ 0
4. Hospital can only update own ICU data
5. JWT token required for all endpoints
```

---

## 📱 UI Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    HOSPITAL DASHBOARD - ICU SECTION                      │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│ 🏥 ICU Bed Management                                                 │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│ Current Status                                                        │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│ │    20    │ │    8     │ │    12    │ │  60.0%   │                │
│ │  Total   │ │Available │ │ Occupied │ │Occupancy │                │
│ │ICU Beds  │ │  (green) │ │  (red)   │ │   Rate   │                │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘                │
│                                                                       │
│ Update ICU Availability                                               │
│ ┌─────────────────────────────────────────────────────────────────┐  │
│ │ Total ICU Beds:      [25      ]                                 │  │
│ │ Available ICU Beds:  [10      ]                                 │  │
│ │                                                                  │  │
│ │ [🔄 Update ICU Beds]                                             │  │
│ └─────────────────────────────────────────────────────────────────┘  │
│                                                                       │
│ ✅ ICU beds updated successfully!                                     │
└───────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    AMBULANCE DASHBOARD - MAP VIEW                        │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│ 📍 Real-Time Location & Nearby Hospitals                              │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│ ┌─────────────────────────────────────────────────────────────────┐  │
│ │                         🗺️ MAP                                   │  │
│ │                                                                  │  │
│ │         🏥 Hospital A                                            │  │
│ │         (ICU: 8/20)                                              │  │
│ │                                                                  │  │
│ │                    🚑 Your Location                              │  │
│ │                                                                  │  │
│ │                           ⭐ Hospital B (Recommended)            │  │
│ │                           (ICU: 12/20)                           │  │
│ │                                                                  │  │
│ │    🏥 Hospital C                                                 │  │
│ │    (ICU: 5/15)                                                   │  │
│ └─────────────────────────────────────────────────────────────────┘  │
│                                                                       │
│ ⭐ Recommended Hospital                                                │
│ ┌─────────────────────────────────────────────────────────────────┐  │
│ │ Hospital B - Fortis Hospital                                     │  │
│ │ 📍 Distance: 3.8 km                                              │  │
│ │ 🛏️ Available Beds: 48                                            │  │
│ │ 🏥 ICU Available: 12/20                                          │  │
│ │ 📊 Current Load: 25                                              │  │
│ │ 🎯 Score: 1.0                                                    │  │
│ └─────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────┘
```

---

**System Status**: ✅ FULLY OPERATIONAL  
**Real-Time Sync**: ✅ ACTIVE  
**ICU Filter**: ✅ ENABLED  
**Production Ready**: ✅ YES
