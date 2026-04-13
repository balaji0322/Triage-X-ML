# 🏗️ TRIAGE-X System Architecture Diagram

## High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          TRIAGE-X SYSTEM                                │
│                   AI-Powered Emergency Response                         │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐                                    ┌──────────────────┐
│   AMBULANCE      │                                    │    HOSPITAL      │
│   Dashboard      │                                    │    Dashboard     │
│   (React)        │                                    │    (React)       │
│                  │                                    │                  │
│  • Patient Form  │                                    │  • Live Cases    │
│  • ML Prediction │                                    │  • WebSocket     │
│  • GPS Location  │                                    │  • Analytics     │
│  • Case Submit   │                                    │  • Filtering     │
└────────┬─────────┘                                    └────────┬─────────┘
         │                                                       │
         │ HTTP/WebSocket                         HTTP/WebSocket│
         │                                                       │
         └───────────────────┬───────────────────────────────────┘
                             │
                             ▼
         ┌───────────────────────────────────────────────────────┐
         │              FASTAPI BACKEND                          │
         │              (Python 3.9+)                            │
         ├───────────────────────────────────────────────────────┤
         │                                                       │
         │  ┌─────────────────────────────────────────────────┐ │
         │  │         API ROUTES (23 Endpoints)               │ │
         │  ├─────────────────────────────────────────────────┤ │
         │  │ • Authentication (4)                            │ │
         │  │ • ML Prediction (3)                             │ │
         │  │ • Case Management (4)                           │ │
         │  │ • Advanced Features (3)                         │ │
         │  │ • GPS Integration (3)                           │ │
         │  │ • WebSocket (2)                                 │ │
         │  │ • Health Check (1)                              │ │
         │  └─────────────────────────────────────────────────┘ │
         │                                                       │
         │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
         │  │ Auth Module  │  │ WebSocket    │  │ GPS Module │ │
         │  │              │  │ Manager      │  │            │ │
         │  │ • JWT        │  │              │  │ • Haversine│ │
         │  │ • bcrypt     │  │ • Broadcast  │  │ • ETA      │ │
         │  │ • RBAC       │  │ • Reconnect  │  │ • Routing  │ │
         │  └──────────────┘  └──────────────┘  └────────────┘ │
         │                                                       │
         │  ┌─────────────────────────────────────────────────┐ │
         │  │         ML ENGINE (XGBoost)                     │ │
         │  ├─────────────────────────────────────────────────┤ │
         │  │ • Model: triage_model.pkl                       │ │
         │  │ • Accuracy: 98%                                 │ │
         │  │ • Features: 28 (17 base + 11 derived)          │ │
         │  │ • Classes: Urgent, Moderate, Minor             │ │
         │  │ • Response: < 100ms                             │ │
         │  └─────────────────────────────────────────────────┘ │
         │                                                       │
         └───────────────────┬───────────────────────────────────┘
                             │
                             ▼
         ┌───────────────────────────────────────────────────────┐
         │              MONGODB DATABASE                         │
         │              (NoSQL)                                  │
         ├───────────────────────────────────────────────────────┤
         │                                                       │
         │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
         │  │ ambulances   │  │  hospitals   │  │   cases    │ │
         │  │              │  │              │  │            │ │
         │  │ • driver     │  │ • hospital_id│  │ • case_id  │ │
         │  │ • amb_number │  │ • name       │  │ • severity │ │
         │  │ • password   │  │ • address    │  │ • vitals   │ │
         │  │              │  │ • password   │  │ • timestamp│ │
         │  │ 2 indexes    │  │ 3 indexes    │  │ 6 indexes  │ │
         │  └──────────────┘  └──────────────┘  └────────────┘ │
         │                                                       │
         │  ┌──────────────────────────────────────────────────┐│
         │  │         ambulance_locations                      ││
         │  │         (GPS Tracking)                           ││
         │  │  • ambulance_id                                  ││
         │  │  • latitude, longitude                           ││
         │  │  • timestamp                                     ││
         │  └──────────────────────────────────────────────────┘│
         └───────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

### 1. Ambulance → Prediction → Hospital

```
┌─────────────┐
│  AMBULANCE  │
│  Dashboard  │
└──────┬──────┘
       │
       │ 1. Enter Patient Data (17 fields)
       │    • Heart Rate, BP, SpO2, Temp, etc.
       │    • Symptoms, Medical History
       │
       ▼
┌─────────────────────────────────────────┐
│  POST /predict                          │
│  ┌───────────────────────────────────┐  │
│  │  ML Model (XGBoost)               │  │
│  │  • Load 17 base features          │  │
│  │  • Generate 11 derived features   │  │
│  │  • Total: 28 features             │  │
│  │  • Predict severity               │  │
│  │  • Calculate confidence           │  │
│  └───────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
                  │ 2. Response
                  │    • Severity: "Urgent"
                  │    • Confidence: 0.92
                  │
                  ▼
┌─────────────────────────────────────────┐
│  POST /api/predict/enhanced             │
│  ┌───────────────────────────────────┐  │
│  │  Enhanced AI Insights             │  │
│  │  • Risk Score: 92/100             │  │
│  │  • Top 3 Factors:                 │  │
│  │    - oxygen_saturation: 88        │  │
│  │    - heart_rate: 110              │  │
│  │    - systolic_bp: 85              │  │
│  │  • Recommendation: "URGENT"       │  │
│  └───────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
                  │ 3. Display Results
                  │
                  ▼
┌─────────────────────────────────────────┐
│  POST /api/suggest-hospital             │
│  ┌───────────────────────────────────┐  │
│  │  Smart Hospital Allocation        │  │
│  │  • Calculate distances            │  │
│  │  • Check hospital loads           │  │
│  │  • Priority scoring:              │  │
│  │    - Severity: 40%                │  │
│  │    - Distance: 35%                │  │
│  │    - Load: 25%                    │  │
│  │  • Return best hospital           │  │
│  └───────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
                  │ 4. Suggested Hospital
                  │    • HOSP-CHE-1234
                  │    • Distance: 5.2 km
                  │    • ETA: 8 minutes
                  │
                  ▼
┌─────────────────────────────────────────┐
│  POST /api/gps/route                    │
│  ┌───────────────────────────────────┐  │
│  │  GPS Route Calculation            │  │
│  │  • Haversine distance             │  │
│  │  • ETA estimation                 │  │
│  │  • Direction guidance             │  │
│  └───────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
                  │ 5. Route Information
                  │
                  ▼
┌─────────────────────────────────────────┐
│  POST /api/send-case                    │
│  ┌───────────────────────────────────┐  │
│  │  Case Submission                  │  │
│  │  • Store in MongoDB               │  │
│  │  • Generate case_id               │  │
│  │  • Set status: "pending"          │  │
│  │  • Calculate risk_score           │  │
│  └───────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
                  │ 6. Broadcast via WebSocket
                  │
                  ▼
┌─────────────────────────────────────────┐
│  WebSocket Manager                      │
│  ┌───────────────────────────────────┐  │
│  │  • Get all hospital connections   │  │
│  │  • Broadcast new case message     │  │
│  │  • Include: severity, vitals, ETA │  │
│  └───────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
                  │ 7. Real-Time Update
                  │
                  ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  HOSPITAL   │   │  HOSPITAL   │   │  HOSPITAL   │
│  Dashboard  │   │  Dashboard  │   │  Dashboard  │
│  #1         │   │  #2         │   │  #3         │
└─────────────┘   └─────────────┘   └─────────────┘
     │                 │                 │
     │ 8. Display Case │                 │
     │    • Severity   │                 │
     │    • Vitals     │                 │
     │    • ETA        │                 │
     │    • Notification                 │
     └─────────────────┴─────────────────┘
```

---

## WebSocket Communication Flow

```
┌──────────────┐                    ┌──────────────┐
│  HOSPITAL    │                    │   BACKEND    │
│  Dashboard   │                    │   Server     │
└──────┬───────┘                    └──────┬───────┘
       │                                   │
       │ 1. Connect                        │
       │ ws://localhost:8000/ws/cases      │
       │ ?role=hospital                    │
       ├──────────────────────────────────>│
       │                                   │
       │ 2. Connection Confirmation        │
       │ {"type": "connection",            │
       │  "status": "connected"}           │
       │<──────────────────────────────────┤
       │                                   │
       │ 3. Heartbeat (every 30s)          │
       │ "ping"                            │
       ├──────────────────────────────────>│
       │                                   │
       │ 4. Pong Response                  │
       │ {"type": "pong"}                  │
       │<──────────────────────────────────┤
       │                                   │
       │                                   │
       │         [New Case Submitted]      │
       │                                   │
       │ 5. New Case Broadcast             │
       │ {"type": "new_case",              │
       │  "case": {                        │
       │    "case_id": "...",              │
       │    "severity": "Urgent",          │
       │    "vitals": {...}                │
       │  }}                               │
       │<──────────────────────────────────┤
       │                                   │
       │ 6. Update UI                      │
       │ • Add to case list                │
       │ • Show notification               │
       │ • Play sound (if urgent)          │
       │                                   │
       │                                   │
       │         [Connection Lost]         │
       │                                   │
       │ 7. Auto-Reconnect                 │
       │ (Attempt 1/5, delay 3s)           │
       ├──────────────────────────────────>│
       │                                   │
       │ 8. Reconnected                    │
       │<──────────────────────────────────┤
       │                                   │
       │                                   │
       │         [Fallback Mode]           │
       │                                   │
       │ 9. Polling (if WS fails)          │
       │ GET /api/cases (every 10s)        │
       ├──────────────────────────────────>│
       │                                   │
       │ 10. Cases Response                │
       │<──────────────────────────────────┤
       │                                   │
```

---

## Authentication Flow

```
┌──────────────┐                    ┌──────────────┐
│    USER      │                    │   BACKEND    │
│  (Ambulance/ │                    │   Server     │
│   Hospital)  │                    │              │
└──────┬───────┘                    └──────┬───────┘
       │                                   │
       │ 1. Signup                         │
       │ POST /api/ambulance/signup        │
       │ {                                 │
       │   "driver_name": "John",          │
       │   "ambulance_number": "AMB-001",  │
       │   "password": "secret"            │
       │ }                                 │
       ├──────────────────────────────────>│
       │                                   │
       │                                   │ 2. Hash Password
       │                                   │    bcrypt.hash(password)
       │                                   │
       │                                   │ 3. Store in MongoDB
       │                                   │    db.ambulances.insert()
       │                                   │
       │                                   │ 4. Generate JWT
       │                                   │    jwt.encode({
       │                                   │      "sub": user_id,
       │                                   │      "role": "ambulance",
       │                                   │      "exp": 24h
       │                                   │    })
       │                                   │
       │ 5. Response                       │
       │ {                                 │
       │   "access_token": "eyJhbG...",    │
       │   "role": "ambulance",            │
       │   "user_data": {...}              │
       │ }                                 │
       │<──────────────────────────────────┤
       │                                   │
       │ 6. Store Token                    │
       │    localStorage.setItem('token')  │
       │                                   │
       │                                   │
       │ 7. Protected Request              │
       │ POST /api/send-case               │
       │ Authorization: Bearer eyJhbG...   │
       ├──────────────────────────────────>│
       │                                   │
       │                                   │ 8. Verify Token
       │                                   │    jwt.decode(token)
       │                                   │    Check expiry
       │                                   │    Check role
       │                                   │
       │                                   │ 9. Process Request
       │                                   │    (if authorized)
       │                                   │
       │ 10. Response                      │
       │<──────────────────────────────────┤
       │                                   │
```

---

## ML Prediction Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    ML PREDICTION PIPELINE                   │
└─────────────────────────────────────────────────────────────┘

INPUT (17 Base Features)
┌─────────────────────────────────────────────────────────────┐
│ • heart_rate          • systolic_bp       • diastolic_bp    │
│ • oxygen_saturation   • temperature       • respiratory_rate│
│ • age                 • gender                              │
│ • chest_pain          • fever             • breathing_diff  │
│ • injury_type         • diabetes          • heart_disease   │
│ • hypertension        • asthma                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              FEATURE ENGINEERING (11 Derived)               │
├─────────────────────────────────────────────────────────────┤
│ 1. pulse_pressure = systolic_bp - diastolic_bp              │
│ 2. mean_arterial_pressure = diastolic + (pulse_pressure/3)  │
│ 3. shock_index = heart_rate / systolic_bp                   │
│ 4. age_risk = (age > 65) ? 1 : 0                            │
│ 5. has_fever = (temperature > 38.0) ? 1 : 0                 │
│ 6. hypoxia = (oxygen_saturation < 92) ? 1 : 0               │
│ 7. tachycardia = (heart_rate > 100) ? 1 : 0                 │
│ 8. tachypnea = (respiratory_rate > 20) ? 1 : 0              │
│ 9. hypotension = (systolic_bp < 90) ? 1 : 0                 │
│ 10. comorbidity_count = diabetes + heart_disease + ...      │
│ 11. critical_symptoms = chest_pain + breathing_diff + ...   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  TOTAL: 28 FEATURES                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              XGBOOST MODEL (triage_model.pkl)               │
├─────────────────────────────────────────────────────────────┤
│ • Algorithm: Gradient Boosting                              │
│ • Trees: 100                                                │
│ • Max Depth: 6                                              │
│ • Learning Rate: 0.1                                        │
│ • Accuracy: 98%                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    PREDICTION OUTPUT                        │
├─────────────────────────────────────────────────────────────┤
│ • Probabilities: [0.92, 0.05, 0.03]                         │
│ • Predicted Class: 0 (Urgent)                               │
│ • Confidence: 0.92                                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  LABEL MAPPING                              │
├─────────────────────────────────────────────────────────────┤
│ 0 → "Urgent"     (Immediate attention required)             │
│ 1 → "Moderate"   (Monitor closely)                          │
│ 2 → "Minor"      (Standard care)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
OUTPUT
┌─────────────────────────────────────────────────────────────┐
│ {                                                           │
│   "severity": "Urgent",                                     │
│   "severity_code": 0,                                       │
│   "confidence": 0.92                                        │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Smart Hospital Allocation Algorithm

```
┌─────────────────────────────────────────────────────────────┐
│           SMART HOSPITAL ALLOCATION ALGORITHM               │
└─────────────────────────────────────────────────────────────┘

INPUT
┌─────────────────────────────────────────────────────────────┐
│ • Severity: "Urgent" (code: 0)                              │
│ • Ambulance Location: (13.0827, 80.2707)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 1: GET ALL HOSPITALS                      │
├─────────────────────────────────────────────────────────────┤
│ db.hospitals.find()                                         │
│ → Hospital A, B, C, D, E                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         STEP 2: CALCULATE DISTANCE (Haversine)              │
├─────────────────────────────────────────────────────────────┤
│ For each hospital:                                          │
│   distance = haversine(ambulance_loc, hospital_loc)         │
│                                                             │
│ Hospital A: 5.2 km                                          │
│ Hospital B: 7.8 km                                          │
│ Hospital C: 12.3 km                                         │
│ Hospital D: 15.6 km                                         │
│ Hospital E: 20.1 km                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│            STEP 3: GET HOSPITAL LOAD                        │
├─────────────────────────────────────────────────────────────┤
│ For each hospital:                                          │
│   load = db.cases.count({                                   │
│     hospital_assigned: hospital_id,                         │
│     status: "pending"                                       │
│   })                                                        │
│                                                             │
│ Hospital A: 3 cases                                         │
│ Hospital B: 5 cases                                         │
│ Hospital C: 2 cases                                         │
│ Hospital D: 8 cases                                         │
│ Hospital E: 1 case                                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         STEP 4: CALCULATE PRIORITY SCORE                    │
├─────────────────────────────────────────────────────────────┤
│ score = severity_weight + distance_weight + load_weight     │
│                                                             │
│ severity_weight = (2 - severity_code) * 40                  │
│   → Urgent (0): 80, Moderate (1): 40, Minor (2): 0         │
│                                                             │
│ distance_weight = min(distance / 50 * 35, 35)               │
│   → Closer = lower score                                    │
│                                                             │
│ load_weight = min(load / 100 * 25, 25)                      │
│   → Less load = lower score                                 │
│                                                             │
│ Hospital A: 80 + 3.64 + 0.75 = 84.39                        │
│ Hospital B: 80 + 5.46 + 1.25 = 86.71                        │
│ Hospital C: 80 + 8.61 + 0.50 = 89.11                        │
│ Hospital D: 80 + 10.92 + 2.00 = 92.92                       │
│ Hospital E: 80 + 14.07 + 0.25 = 94.32                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 5: SORT BY SCORE (Lower = Better)         │
├─────────────────────────────────────────────────────────────┤
│ 1. Hospital A: 84.39 ← BEST MATCH                           │
│ 2. Hospital B: 86.71                                        │
│ 3. Hospital C: 89.11                                        │
│ 4. Hospital D: 92.92                                        │
│ 5. Hospital E: 94.32                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
OUTPUT
┌─────────────────────────────────────────────────────────────┐
│ {                                                           │
│   "suggested_hospital_id": "HOSP-CHE-1234",                 │
│   "hospital_name": "Hospital A",                            │
│   "distance_km": 5.2,                                       │
│   "current_load": 3,                                        │
│   "priority_score": 84.39,                                  │
│   "reason": "Best match: 5.2km away, 3 active cases.        │
│              URGENT case - closest available hospital.",    │
│   "alternatives": [Hospital B, C, D]                        │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    TECHNOLOGY STACK                         │
└─────────────────────────────────────────────────────────────┘

FRONTEND
┌─────────────────────────────────────────────────────────────┐
│ React 18                                                    │
│ ├─ React Router v6        (Routing)                         │
│ ├─ Axios                  (HTTP Client)                     │
│ ├─ WebSocket API          (Real-time)                       │
│ ├─ Chart.js               (Analytics Charts)                │
│ └─ CSS3                   (Responsive Design)               │
└─────────────────────────────────────────────────────────────┘

BACKEND
┌─────────────────────────────────────────────────────────────┐
│ FastAPI 0.110.0                                             │
│ ├─ Uvicorn                (ASGI Server)                     │
│ ├─ Pydantic 2.7.0         (Validation)                      │
│ ├─ python-jose            (JWT)                             │
│ ├─ passlib + bcrypt       (Password Hashing)                │
│ ├─ Loguru                 (Logging)                         │
│ └─ WebSockets 12.0        (Real-time)                       │
└─────────────────────────────────────────────────────────────┘

MACHINE LEARNING
┌─────────────────────────────────────────────────────────────┐
│ XGBoost 2.0.3                                               │
│ ├─ scikit-learn 1.5.0     (Pipeline, Preprocessing)         │
│ ├─ pandas 2.2.2           (Data Manipulation)               │
│ ├─ numpy 1.26.4           (Numerical Computing)             │
│ ├─ joblib 1.4.2           (Model Serialization)             │
│ └─ SHAP 0.45.1            (Explainability)                  │
└─────────────────────────────────────────────────────────────┘

DATABASE
┌─────────────────────────────────────────────────────────────┐
│ MongoDB 4.4+                                                │
│ ├─ PyMongo 4.6.3          (Python Driver)                   │
│ ├─ Indexes                (Performance)                     │
│ └─ Aggregation Pipeline   (Analytics)                       │
└─────────────────────────────────────────────────────────────┘

DEPLOYMENT
┌─────────────────────────────────────────────────────────────┐
│ Docker                    (Containerization)                │
│ Gunicorn                  (Production Server)               │
│ Nginx                     (Reverse Proxy)                   │
│ PM2                       (Process Manager)                 │
└─────────────────────────────────────────────────────────────┘
```

---

**System Architecture Version**: 0.2.0  
**Last Updated**: April 13, 2026  
**Status**: Production Ready
