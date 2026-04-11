# 🏗️ TRIAGE-X System Architecture

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│                     http://localhost:3000                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Login Page   │  │  Ambulance   │  │   Hospital   │          │
│  │              │  │   Signup     │  │    Signup    │          │
│  │ - Ambulance  │  └──────────────┘  └──────────────┘          │
│  │ - Hospital   │                                                │
│  └──────────────┘                                                │
│                                                                   │
│  ┌──────────────────────────────┐  ┌──────────────────────────┐│
│  │   Ambulance Dashboard        │  │   Hospital Dashboard     ││
│  │                              │  │                          ││
│  │  - Patient Input Form        │  │  - Severity Stats        ││
│  │  - ML Prediction Display     │  │  - Case Filtering        ││
│  │  - Send Case Button          │  │  - Live Cases Table      ││
│  │  - Recent Cases (Last 5)     │  │  - Auto-refresh (10s)    ││
│  └──────────────────────────────┘  └──────────────────────────┘│
│                                                                   │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            │ JWT Bearer Token
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│                      BACKEND (FastAPI)                            │
│                   http://localhost:8000                           │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    API ENDPOINTS                             ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  PUBLIC ROUTES                                               ││
│  │  • POST /api/ambulance/signup                                ││
│  │  • POST /api/ambulance/login                                 ││
│  │  • POST /api/hospital/signup                                 ││
│  │  • POST /api/hospital/login                                  ││
│  │  • POST /predict (ML Model)                                  ││
│  │  • GET  /ping                                                ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  PROTECTED ROUTES (Ambulance)                                ││
│  │  • POST /api/send-case                                       ││
│  │  • GET  /api/ambulance/recent-cases                          ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  PROTECTED ROUTES (Hospital)                                 ││
│  │  • GET  /api/cases                                           ││
│  │  • GET  /api/hospital/stats                                  ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  AUTHENTICATION LAYER                        ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  • JWT Token Generation & Verification                       ││
│  │  • Bcrypt Password Hashing                                   ││
│  │  • Role-Based Access Control (RBAC)                          ││
│  │  • Token Expiry: 24 hours                                    ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    ML MODEL LAYER                            ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  • Load triage_model.pkl (EXISTING - UNCHANGED)              ││
│  │  • Load label_map.pkl                                        ││
│  │  • Load feature_importance.pkl                               ││
│  │  • Predict severity from patient data                        ││
│  │  • Return: severity, confidence, severity_code               ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            │ PyMongo
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│                      DATABASE (MongoDB)                           │
│                   mongodb://localhost:27017                       │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐│
│  │   ambulances     │  │    hospitals     │  │     cases      ││
│  ├──────────────────┤  ├──────────────────┤  ├────────────────┤│
│  │ _id              │  │ hospital_id      │  │ case_id        ││
│  │ driver_name      │  │ hospital_name    │  │ ambulance_num  ││
│  │ ambulance_number │  │ address          │  │ driver_name    ││
│  │ password_hash    │  │ password_hash    │  │ patient_data   ││
│  │ created_at       │  │ created_at       │  │ severity       ││
│  │                  │  │                  │  │ confidence     ││
│  │ INDEX: unique    │  │ INDEX: unique    │  │ timestamp      ││
│  │   ambulance_num  │  │   hospital_id    │  │ status         ││
│  └──────────────────┘  └──────────────────┘  └────────────────┘│
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagrams

### 1. Ambulance Registration Flow
```
┌─────────┐
│  User   │
└────┬────┘
     │ 1. Fill signup form
     │    (driver_name, ambulance_number, password)
     ▼
┌─────────────────┐
│  Frontend Form  │
└────┬────────────┘
     │ 2. POST /api/ambulance/signup
     ▼
┌─────────────────────────┐
│  Backend Validation     │
│  - Check unique number  │
│  - Hash password        │
└────┬────────────────────┘
     │ 3. Insert to MongoDB
     ▼
┌─────────────────┐
│  ambulances     │
│  collection     │
└────┬────────────┘
     │ 4. Generate JWT token
     ▼
┌─────────────────┐
│  Return token   │
│  + user data    │
└────┬────────────┘
     │ 5. Store in localStorage
     ▼
┌─────────────────┐
│  Redirect to    │
│  Dashboard      │
└─────────────────┘
```

### 2. Hospital Registration Flow
```
┌─────────┐
│  User   │
└────┬────┘
     │ 1. Fill signup form
     │    (hospital_name, address, password)
     ▼
┌─────────────────┐
│  Frontend Form  │
└────┬────────────┘
     │ 2. POST /api/hospital/signup
     ▼
┌─────────────────────────────┐
│  Backend Processing         │
│  - Generate Hospital ID     │
│    Format: HOSP-{CITY}-1234 │
│  - Hash password            │
└────┬────────────────────────┘
     │ 3. Insert to MongoDB
     ▼
┌─────────────────┐
│  hospitals      │
│  collection     │
└────┬────────────┘
     │ 4. Generate JWT token
     ▼
┌─────────────────┐
│  Return token   │
│  + hospital_id  │
└────┬────────────┘
     │ 5. Display Hospital ID (3 seconds)
     │ 6. Store in localStorage
     ▼
┌─────────────────┐
│  Redirect to    │
│  Dashboard      │
└─────────────────┘
```

### 3. ML Prediction & Case Submission Flow
```
┌──────────────┐
│  Ambulance   │
│  Dashboard   │
└──────┬───────┘
       │ 1. Enter patient data
       │    (15 features)
       ▼
┌──────────────────┐
│  Patient Form    │
└──────┬───────────┘
       │ 2. Click "Predict"
       │    POST /predict
       ▼
┌──────────────────────────┐
│  Backend ML Layer        │
│  - Load triage_model.pkl │
│  - Predict severity      │
└──────┬───────────────────┘
       │ 3. Return prediction
       │    {severity, confidence}
       ▼
┌──────────────────┐
│  Display Result  │
│  (Color-coded)   │
└──────┬───────────┘
       │ 4. Click "Send Case"
       │    POST /api/send-case
       │    (JWT token required)
       ▼
┌──────────────────────┐
│  Backend Auth Check  │
│  - Verify JWT        │
│  - Check role        │
└──────┬───────────────┘
       │ 5. Store case
       ▼
┌──────────────────┐
│  cases           │
│  collection      │
└──────┬───────────┘
       │ 6. Success response
       ▼
┌──────────────────┐
│  Update UI       │
│  - Clear form    │
│  - Show success  │
│  - Refresh list  │
└──────────────────┘
```

### 4. Hospital Dashboard Real-Time Updates
```
┌──────────────┐
│  Hospital    │
│  Dashboard   │
└──────┬───────┘
       │ 1. Load dashboard
       │    GET /api/cases (JWT)
       │    GET /api/hospital/stats (JWT)
       ▼
┌──────────────────────┐
│  Backend Auth Check  │
│  - Verify JWT        │
│  - Check role        │
└──────┬───────────────┘
       │ 2. Query MongoDB
       ▼
┌──────────────────┐
│  cases           │
│  collection      │
└──────┬───────────┘
       │ 3. Return data
       ▼
┌──────────────────┐
│  Display:        │
│  - Stats cards   │
│  - Cases table   │
│  - Filters       │
└──────┬───────────┘
       │ 4. Auto-refresh (10s)
       │    Repeat steps 1-3
       ▼
┌──────────────────┐
│  Update UI       │
│  (New cases)     │
└──────────────────┘
```

---

## 🔐 Authentication Flow

### JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "role": "ambulance" | "hospital",
    "ambulance_number": "AMB-001",  // for ambulance
    "hospital_id": "HOSP-NEW-1234", // for hospital
    "exp": 1234567890
  },
  "signature": "..."
}
```

### Request Flow with JWT
```
┌─────────────┐
│  Frontend   │
└──────┬──────┘
       │ 1. API call
       │    axios.get('/api/cases')
       ▼
┌──────────────────────┐
│  Axios Interceptor   │
│  - Get token from    │
│    localStorage      │
│  - Add to header:    │
│    Authorization:    │
│    Bearer <token>    │
└──────┬───────────────┘
       │ 2. HTTP request
       ▼
┌──────────────────────┐
│  Backend Middleware  │
│  - Extract token     │
│  - Verify signature  │
│  - Check expiry      │
│  - Decode payload    │
└──────┬───────────────┘
       │ 3a. Valid token
       ▼
┌──────────────────────┐
│  Check Role          │
│  - Match required    │
│    role              │
└──────┬───────────────┘
       │ 4. Access granted
       ▼
┌──────────────────────┐
│  Execute Endpoint    │
│  - Query database    │
│  - Return data       │
└──────┬───────────────┘
       │ 5. Response
       ▼
┌──────────────────────┐
│  Frontend            │
│  - Update UI         │
└──────────────────────┘

       │ 3b. Invalid token
       ▼
┌──────────────────────┐
│  Return 401          │
└──────┬───────────────┘
       │ 4. Interceptor catches
       ▼
┌──────────────────────┐
│  Clear localStorage  │
│  Redirect to /login  │
└──────────────────────┘
```

---

## 🗂️ Component Hierarchy

### Frontend Component Tree
```
App
├── Router
    ├── LoginPage
    │   ├── Ambulance Tab
    │   └── Hospital Tab
    │
    ├── AmbulanceSignup
    │   └── Signup Form
    │
    ├── HospitalSignup
    │   └── Signup Form
    │
    ├── AmbulanceDashboard (Protected)
    │   ├── Header
    │   │   ├── Title
    │   │   └── User Info + Logout
    │   ├── Patient Form
    │   │   ├── Vitals Section
    │   │   ├── Symptoms Section
    │   │   └── Medical History Section
    │   ├── Prediction Card
    │   │   ├── Severity Display
    │   │   └── Send Button
    │   └── Recent Cases
    │       └── Case List
    │
    └── HospitalDashboard (Protected)
        ├── Header
        │   ├── Title
        │   └── User Info + Logout
        ├── Stats Grid
        │   ├── Immediate Card
        │   ├── Urgent Card
        │   ├── Moderate Card
        │   ├── Minor Card
        │   └── Total Card
        ├── Filter Buttons
        └── Cases Table
            └── Case Rows
```

---

## 🔌 API Integration Points

### Frontend → Backend Communication
```
┌─────────────────────────────────────────────────────────────┐
│                    API CALLS (api.js)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Authentication (No Token)                                  │
│  ├── ambulanceSignup(data)                                 │
│  ├── ambulanceLogin(data)                                  │
│  ├── hospitalSignup(data)                                  │
│  └── hospitalLogin(data)                                   │
│                                                             │
│  ML Prediction (No Token)                                  │
│  └── predictSeverity(patientData)                          │
│                                                             │
│  Cases (With Token)                                        │
│  ├── sendCase(data)           [Ambulance only]            │
│  ├── getAmbulanceRecentCases() [Ambulance only]            │
│  ├── getCases()                [Hospital only]             │
│  └── getHospitalStats()        [Hospital only]             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 UI State Management

### LocalStorage Structure
```javascript
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "ambulance" | "hospital",
  "user": {
    // Ambulance
    "id": "uuid",
    "driver_name": "John Doe",
    "ambulance_number": "AMB-001"
    
    // OR Hospital
    "hospital_id": "HOSP-NEW-1234",
    "hospital_name": "City General",
    "address": "123 Main St"
  }
}
```

### Component State Flow
```
LoginPage
  ↓ (on success)
  Store: token, role, user
  ↓
  Navigate to dashboard
  ↓
Dashboard (useEffect)
  ↓
  Check localStorage
  ↓
  If no token → redirect to /login
  ↓
  If token exists → load data
  ↓
  Make API calls with token
  ↓
  Update component state
  ↓
  Render UI
```

---

## 🔄 Real-Time Update Mechanism

### Hospital Dashboard Auto-Refresh
```
┌─────────────────────┐
│  Component Mount    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Initial Load       │
│  - getCases()       │
│  - getStats()       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Set Interval       │
│  (10 seconds)       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Repeat API Calls   │
│  - getCases()       │
│  - getStats()       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Update State       │
│  - setCases()       │
│  - setStats()       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Re-render UI       │
│  (New cases appear) │
└──────┬──────────────┘
       │
       │ (loop continues)
       └──────────────────┐
                          │
       ┌──────────────────┘
       │
       ▼
┌─────────────────────┐
│  Component Unmount  │
│  - Clear interval   │
└─────────────────────┘
```

---

## 📦 Deployment Architecture

### Production Setup
```
┌─────────────────────────────────────────────────────────────┐
│                         INTERNET                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      LOAD BALANCER                          │
│                      (nginx/AWS ALB)                        │
└────────┬────────────────────────────────────┬───────────────┘
         │                                    │
         ▼                                    ▼
┌──────────────────┐              ┌──────────────────┐
│  Frontend        │              │  Backend         │
│  (React Build)   │              │  (FastAPI)       │
│                  │              │                  │
│  - Static files  │              │  - Uvicorn       │
│  - Nginx/S3      │              │  - Gunicorn      │
│  - CDN           │              │  - Docker        │
└──────────────────┘              └────────┬─────────┘
                                           │
                                           ▼
                                  ┌──────────────────┐
                                  │  MongoDB Atlas   │
                                  │  (Cloud)         │
                                  │                  │
                                  │  - Replica Set   │
                                  │  - Auto-backup   │
                                  │  - Monitoring    │
                                  └──────────────────┘
```

---

## 🎯 Summary

This architecture provides:
- ✅ Clear separation of concerns
- ✅ Scalable component structure
- ✅ Secure authentication flow
- ✅ Real-time data updates
- ✅ Role-based access control
- ✅ Production-ready design

**All while keeping the ML model completely untouched!**
