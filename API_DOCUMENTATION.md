# 📡 TRIAGE-X API Documentation

## Base URL
```
Development: http://localhost:8000
Production: https://api.yourdomain.com
```

---

## 🔐 Authentication

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <token>
```

### Roles
- **ambulance**: Can submit cases, get predictions
- **hospital**: Can view cases, access analytics

---

## 📋 API Endpoints

### 1. Health Check

#### GET `/ping`
Health check endpoint.

**Response:**
```json
{
  "msg": "pong",
  "status": "healthy"
}
```

---

### 2. Authentication Endpoints

#### POST `/api/ambulance/signup`
Register new ambulance.

**Request Body:**
```json
{
  "driver_name": "John Doe",
  "ambulance_number": "AMB-001",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "ambulance",
  "user_data": {
    "id": "uuid",
    "driver_name": "John Doe",
    "ambulance_number": "AMB-001"
  }
}
```

#### POST `/api/ambulance/login`
Login for ambulance.

**Request Body:**
```json
{
  "ambulance_number": "AMB-001",
  "password": "secure_password"
}
```

**Response:** Same as signup

#### POST `/api/hospital/signup`
Register new hospital.

**Request Body:**
```json
{
  "hospital_name": "City General Hospital",
  "address": "Chennai, Tamil Nadu",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "hospital",
  "user_data": {
    "hospital_id": "HOSP-CHE-1234",
    "hospital_name": "City General Hospital",
    "address": "Chennai, Tamil Nadu"
  }
}
```

#### POST `/api/hospital/login`
Login for hospital.

**Request Body:**
```json
{
  "hospital_id": "HOSP-CHE-1234",
  "password": "secure_password"
}
```

**Response:** Same as signup

---

### 3. ML Prediction Endpoints

#### POST `/predict`
Predict patient triage severity using ML model.

**Request Body:**
```json
{
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
```

**Response:**
```json
{
  "severity": "Urgent",
  "severity_code": 0,
  "confidence": 0.9234
}
```

**Severity Levels:**
- `Urgent` (code 0): Immediate attention required
- `Moderate` (code 1): Monitor closely
- `Minor` (code 2): Standard care

#### GET `/feature_importance`
Get global feature importance from ML model.

**Response:**
```json
{
  "importance": [
    ["oxygen_saturation", 0.234],
    ["heart_rate", 0.189],
    ["systolic_bp", 0.156],
    ...
  ]
}
```

#### POST `/explain`
Get SHAP explanation for specific prediction.

**Request Body:** Same as `/predict`

**Response:**
```json
{
  "predicted_class": "Urgent",
  "predicted_code": 0,
  "feature_importance": {
    "oxygen_saturation": -0.45,
    "heart_rate": 0.32,
    ...
  },
  "base_value": 0.33
}
```

---

### 4. Case Management

#### POST `/api/send-case`
Send case from ambulance to hospital (requires ambulance auth).

**Request Body:**
```json
{
  "patient_data": {
    "heart_rate": 110,
    "systolic_bp": 85,
    ...
  },
  "severity": "Urgent",
  "confidence": 0.9234
}
```

**Response:**
```json
{
  "case_id": "uuid",
  "ambulance_number": "AMB-001",
  "driver_name": "John Doe",
  "patient_data": {...},
  "severity": "Urgent",
  "confidence": 0.9234,
  "timestamp": "2024-04-13T12:00:00",
  "status": "pending",
  "risk_score": 92
}
```

**Side Effect:** Broadcasts case to all connected hospitals via WebSocket

#### GET `/api/cases?limit=50`
Get all cases (requires hospital auth).

**Query Parameters:**
- `limit` (optional): Number of cases to return (default: 50)

**Response:**
```json
[
  {
    "case_id": "uuid",
    "ambulance_number": "AMB-001",
    "driver_name": "John Doe",
    "patient_data": {...},
    "severity": "Urgent",
    "confidence": 0.9234,
    "timestamp": "2024-04-13T12:00:00",
    "status": "pending"
  },
  ...
]
```

#### GET `/api/ambulance/recent-cases?limit=5`
Get recent cases for current ambulance (requires ambulance auth).

**Response:** Same format as `/api/cases`

#### GET `/api/hospital/stats`
Get severity statistics (requires hospital auth).

**Response:**
```json
{
  "Urgent": 15,
  "Moderate": 23,
  "Minor": 42,
  "total": 80
}
```

---

### 5. Advanced Features

#### POST `/api/suggest-hospital`
Smart hospital allocation (requires ambulance auth).

**Request Body:**
```json
{
  "severity": "Urgent",
  "severity_code": 0,
  "ambulance_lat": 13.0827,
  "ambulance_lon": 80.2707
}
```

**Response:**
```json
{
  "suggested_hospital_id": "HOSP-CHE-1234",
  "hospital_name": "City General Hospital",
  "distance_km": 5.2,
  "current_load": 3,
  "priority_score": 45.6,
  "reason": "Best match: 5.2km away, 3 active cases. URGENT case - closest available hospital selected.",
  "alternatives": [
    {
      "hospital_id": "HOSP-CHE-5678",
      "hospital_name": "Metro Hospital",
      "distance_km": 7.8,
      "load": 5
    },
    ...
  ]
}
```

**Algorithm:**
- Priority Score = Severity Weight (40%) + Distance Weight (35%) + Load Weight (25%)
- Lower score = better choice

#### POST `/api/predict/enhanced`
Enhanced prediction with AI insights.

**Request Body:** Same as `/predict`

**Response:**
```json
{
  "severity": "Urgent",
  "severity_code": 0,
  "confidence": 0.9234,
  "risk_score": 92,
  "top_factors": [
    {
      "feature": "oxygen_saturation",
      "importance": 0.234,
      "value": 88
    },
    {
      "feature": "heart_rate",
      "importance": 0.189,
      "value": 110
    },
    {
      "feature": "systolic_bp",
      "importance": 0.156,
      "value": 85
    }
  ],
  "recommendation": "🚨 IMMEDIATE ATTENTION REQUIRED. Prepare emergency protocols."
}
```

#### GET `/api/analytics`
Get comprehensive analytics (requires hospital auth).

**Response:**
```json
{
  "total_cases": 150,
  "cases_by_severity": {
    "Urgent": 25,
    "Moderate": 45,
    "Minor": 80
  },
  "peak_hours": [
    {"hour": 14, "cases": 23},
    {"hour": 10, "cases": 19},
    ...
  ],
  "average_severity_score": 1.8,
  "cases_last_24h": 32,
  "trend": "📈 Increasing (+15.2%)"
}
```

---

### 6. GPS Integration

#### POST `/api/gps/route`
Calculate route from ambulance to hospital (requires ambulance auth).

**Request Body:**
```json
{
  "ambulance_location": {
    "latitude": 13.0827,
    "longitude": 80.2707
  },
  "hospital_id": "HOSP-CHE-1234"
}
```

**Response:**
```json
{
  "hospital_id": "HOSP-CHE-1234",
  "hospital_name": "City General Hospital",
  "hospital_location": {
    "latitude": 13.0878,
    "longitude": 80.2785
  },
  "distance_km": 5.2,
  "estimated_time_minutes": 8,
  "route_description": "Head Northeast for 5.2 km. Estimated arrival: 8 minutes. Destination: City General Hospital"
}
```

#### POST `/api/gps/nearest-hospitals`
Find nearest hospitals (requires ambulance auth).

**Request Body:**
```json
{
  "ambulance_location": {
    "latitude": 13.0827,
    "longitude": 80.2707
  },
  "severity": "Urgent",
  "limit": 5
}
```

**Response:**
```json
{
  "hospitals": [
    {
      "hospital_id": "HOSP-CHE-1234",
      "hospital_name": "City General Hospital",
      "address": "Chennai, Tamil Nadu",
      "distance_km": 5.2,
      "eta_minutes": 8,
      "current_load": 3,
      "coordinates": {
        "latitude": 13.0878,
        "longitude": 80.2785
      }
    },
    ...
  ],
  "ambulance_location": {
    "latitude": 13.0827,
    "longitude": 80.2707
  }
}
```

#### POST `/api/gps/update-location`
Update ambulance real-time location (requires ambulance auth).

**Request Body:**
```json
{
  "latitude": 13.0827,
  "longitude": 80.2707
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Location updated",
  "location": {
    "latitude": 13.0827,
    "longitude": 80.2707
  }
}
```

---

### 7. WebSocket

#### WS `/ws/cases?role=hospital`
Real-time case updates via WebSocket.

**Query Parameters:**
- `role`: "hospital" or "ambulance"

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/cases?role=hospital');
```

**Messages Received:**
```json
// Connection confirmation
{
  "type": "connection",
  "status": "connected",
  "role": "hospital",
  "message": "Connected as hospital",
  "active_connections": 5
}

// New case broadcast
{
  "type": "new_case",
  "case": {
    "case_id": "uuid",
    "ambulance_number": "AMB-001",
    "driver_name": "John Doe",
    "severity": "Urgent",
    "confidence": 0.9234,
    "timestamp": "2024-04-13T12:00:00",
    "status": "pending",
    "patient_age": 75,
    "patient_vitals": {
      "heart_rate": 110,
      "oxygen_saturation": 88,
      "systolic_bp": 85
    }
  }
}

// Pong response
{
  "type": "pong",
  "timestamp": "2024-04-13T12:00:00"
}
```

**Messages Sent:**
```javascript
// Heartbeat
ws.send('ping');
```

#### GET `/ws/status`
Get WebSocket connection status.

**Response:**
```json
{
  "hospital_connections": 5,
  "ambulance_connections": 2,
  "total_connections": 7
}
```

---

## 🔒 Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Ambulance access required"
}
```

### 404 Not Found
```json
{
  "detail": "Hospital not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Prediction error: <error message>"
}
```

---

## 📊 Rate Limiting

**Current Limits:**
- Prediction: 100 requests/minute
- Authentication: 10 requests/minute
- WebSocket: 1000 messages/minute

---

## 🧪 Testing Examples

### cURL Examples

```bash
# Health check
curl http://localhost:8000/ping

# Ambulance signup
curl -X POST http://localhost:8000/api/ambulance/signup \
  -H "Content-Type: application/json" \
  -d '{"driver_name":"John","ambulance_number":"AMB-001","password":"test123"}'

# Prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"heart_rate":110,"systolic_bp":85,"diastolic_bp":60,"oxygen_saturation":88,"temperature":39.2,"respiratory_rate":28,"age":75,"gender":"male","chest_pain":1,"fever":1,"breathing_difficulty":1,"injury_type":0,"diabetes":1,"heart_disease":1,"hypertension":1,"asthma":0}'

# Send case (with auth)
curl -X POST http://localhost:8000/api/send-case \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"patient_data":{...},"severity":"Urgent","confidence":0.92}'
```

### Python Examples

```python
import requests

# Ambulance signup
response = requests.post('http://localhost:8000/api/ambulance/signup', json={
    'driver_name': 'John Doe',
    'ambulance_number': 'AMB-001',
    'password': 'test123'
})
token = response.json()['access_token']

# Prediction
response = requests.post('http://localhost:8000/predict', json={
    'heart_rate': 110,
    'systolic_bp': 85,
    # ... other fields
})
prediction = response.json()

# Send case
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:8000/api/send-case', 
    headers=headers,
    json={
        'patient_data': {...},
        'severity': prediction['severity'],
        'confidence': prediction['confidence']
    }
)
```

### JavaScript Examples

```javascript
// Ambulance signup
const response = await fetch('http://localhost:8000/api/ambulance/signup', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    driver_name: 'John Doe',
    ambulance_number: 'AMB-001',
    password: 'test123'
  })
});
const {access_token} = await response.json();

// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/cases?role=hospital');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

---

## 📚 Interactive Documentation

Visit these URLs for interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

**API Version**: 0.2.0
**Last Updated**: 2024-04-13
