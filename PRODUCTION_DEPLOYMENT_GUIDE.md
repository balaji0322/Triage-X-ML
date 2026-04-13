# 🚀 TRIAGE-X Production Deployment Guide

## System Overview

**TRIAGE-X** is an AI-powered emergency response system that provides:
- Real-time patient triage using ML (XGBoost)
- Smart hospital allocation based on distance, load, and severity
- WebSocket-based real-time communication
- GPS integration for routing and ETA calculation
- Comprehensive analytics dashboard
- JWT-based authentication

---

## ✅ Pre-Deployment Checklist

### 1. System Requirements
- **Python**: 3.9+
- **Node.js**: 16+
- **MongoDB**: 4.4+
- **RAM**: 4GB minimum
- **Storage**: 2GB minimum

### 2. Environment Setup

#### Backend (.env)
```bash
# MongoDB
MONGO_URL=mongodb://localhost:27017/
DB_NAME=triage_system

# Security
SECRET_KEY=your-production-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API
API_HOST=0.0.0.0
API_PORT=8000

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

#### Frontend (.env)
```bash
REACT_APP_API_URL=http://localhost:8000
```

---

## 🔧 Installation Steps

### Step 1: Install Dependencies

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

### Step 2: Start MongoDB
```bash
# Linux/Mac
sudo systemctl start mongod

# Windows
net start MongoDB

# Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Step 3: Verify ML Model
```bash
cd backend
python -c "from app.utils import load_artifacts; load_artifacts(); print('✅ Model loaded')"
```

### Step 4: Run Production Verification
```bash
cd backend
python production_verification.py
```

Expected output:
```
✅ PASS - ML Model
✅ PASS - Database
✅ PASS - Prediction
✅ PASS - Authentication
✅ PASS - WebSocket
✅ PASS - Advanced Features
✅ PASS - API Endpoints
🎉 ALL SYSTEMS OPERATIONAL - PRODUCTION READY!
```

---

## 🚀 Starting the System

### Development Mode

#### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate
python run_server.py
```

#### Terminal 2: Frontend
```bash
cd frontend
npm start
```

### Production Mode

#### Backend (with Gunicorn)
```bash
cd backend
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

#### Frontend (Build & Serve)
```bash
cd frontend
npm run build
npx serve -s build -l 3000
```

---

## 🔐 Security Configuration

### 1. Change Default Secret Key
```python
# backend/app/auth.py
SECRET_KEY = os.getenv("SECRET_KEY", "your-production-secret-key")
```

### 2. Configure CORS
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. Enable HTTPS
Use nginx or Apache as reverse proxy:

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 📊 System Architecture

### Backend Components
1. **FastAPI Server** (`main.py`)
   - REST API endpoints
   - WebSocket server
   - ML model integration

2. **ML Model** (`model.py`, `utils.py`)
   - XGBoost classifier
   - Feature engineering
   - Prediction pipeline

3. **Authentication** (`auth.py`, `auth_routes.py`)
   - JWT tokens
   - bcrypt password hashing
   - Role-based access control

4. **Database** (`database.py`)
   - MongoDB connection
   - Collections: ambulances, hospitals, cases
   - Indexed queries

5. **WebSocket** (`websocket_routes.py`, `websocket_manager.py`)
   - Real-time case broadcasting
   - Connection management
   - Auto-reconnect

6. **Advanced Features** (`advanced_features.py`)
   - Smart hospital allocation
   - Enhanced AI insights
   - Analytics dashboard

7. **GPS Integration** (`gps_integration.py`)
   - Distance calculation (Haversine)
   - ETA estimation
   - Nearest hospital search

### Frontend Components
1. **Authentication Pages**
   - LoginPage.jsx
   - AmbulanceSignup.jsx
   - HospitalSignup.jsx

2. **Dashboards**
   - AmbulanceDashboard.jsx (Patient input, prediction)
   - HospitalDashboard.jsx (Real-time cases, WebSocket)
   - AdminDashboard.jsx (Analytics, charts)

3. **API Integration** (`api.js`)
   - Axios instance with auth interceptor
   - WebSocketManager class
   - All API calls

---

## 🧪 Testing

### 1. API Testing
```bash
# Health check
curl http://localhost:8000/ping

# Prediction test
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "heart_rate": 110,
    "systolic_bp": 85,
    "diastolic_bp": 60,
    "oxygen_saturation": 88,
    "temperature": 39.2,
    "respiratory_rate": 28,
    "age": 75,
    "chest_pain": 1,
    "fever": 1,
    "breathing_difficulty": 1,
    "injury_type": 0,
    "diabetes": 1,
    "heart_disease": 1,
    "hypertension": 1,
    "asthma": 0,
    "gender": "male"
  }'
```

### 2. WebSocket Testing
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/cases?role=hospital');
ws.onmessage = (event) => console.log('Received:', event.data);
ws.send('ping');
```

### 3. Integration Testing
```bash
cd backend
python test_integration.py
python test_advanced_features.py
```

---

## 📈 Performance Optimization

### 1. Database Indexing
Already configured in `database.py`:
- ambulance_number (unique)
- hospital_id (unique)
- case_id (unique)
- timestamp, severity, hospital_assigned

### 2. Model Loading
Model loaded ONCE at startup (singleton pattern in `utils.py`)

### 3. Connection Pooling
MongoDB connection pool configured automatically

### 4. Caching
Consider adding Redis for:
- Session management
- Frequently accessed data
- Rate limiting

---

## 🔍 Monitoring & Logging

### Logs Location
- **Backend**: `backend/logs/`
- **Access logs**: `logs/access.log`
- **Error logs**: `logs/error.log`

### Log Levels
```python
# backend/app/logger.py
from loguru import logger

logger.add("logs/app.log", rotation="500 MB", retention="10 days")
```

### Monitoring Endpoints
- `/ping` - Health check
- `/ws/status` - WebSocket connection count
- `/api/analytics` - System analytics

---

## 🚨 Troubleshooting

### Issue: Model not loading
```bash
# Check model files exist
ls -la backend/models/
# Should show: triage_model.pkl, label_map.pkl, feature_importance.pkl

# Regenerate if missing
cd backend
python app/train_model.py
```

### Issue: MongoDB connection failed
```bash
# Check MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# Check connection string
echo $MONGO_URL
```

### Issue: WebSocket not connecting
- Check CORS settings
- Verify WebSocket URL (ws:// not http://)
- Check firewall rules

### Issue: Prediction errors
- Verify all 17 input features provided
- Check feature ranges (age: 0-120, HR: 30-250, etc.)
- Review logs for detailed error messages

---

## 📦 Docker Deployment

### Dockerfile (Backend)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=mongodb://mongodb:27017/
    depends_on:
      - mongodb

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000

volumes:
  mongo_data:
```

---

## 🎯 System Flow

### Complete User Journey

1. **Ambulance Registration**
   - POST `/api/ambulance/signup`
   - Receives JWT token
   - Redirects to dashboard

2. **Patient Assessment**
   - Enter patient vitals
   - POST `/predict` → ML model inference
   - Display severity + confidence

3. **Hospital Allocation**
   - POST `/api/suggest-hospital`
   - Algorithm: severity (40%) + distance (35%) + load (25%)
   - Returns best hospital

4. **Case Submission**
   - POST `/api/send-case`
   - Stores in MongoDB
   - Broadcasts via WebSocket to all hospitals

5. **Hospital Reception**
   - WebSocket receives new case
   - Updates dashboard in real-time
   - Shows severity, vitals, ETA

6. **Analytics**
   - GET `/api/analytics`
   - Aggregates data from MongoDB
   - Shows trends, peak hours, severity distribution

---

## 🔄 Backup & Recovery

### Database Backup
```bash
# Backup
mongodump --db triage_system --out /backup/$(date +%Y%m%d)

# Restore
mongorestore --db triage_system /backup/20240413/triage_system
```

### Model Backup
```bash
# Backup models
tar -czf models_backup_$(date +%Y%m%d).tar.gz backend/models/

# Restore
tar -xzf models_backup_20240413.tar.gz -C backend/
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks
1. **Daily**: Check logs for errors
2. **Weekly**: Review analytics, monitor performance
3. **Monthly**: Database backup, update dependencies
4. **Quarterly**: Security audit, model retraining

### Performance Metrics
- **API Response Time**: < 200ms (prediction)
- **WebSocket Latency**: < 50ms
- **Model Accuracy**: > 95%
- **System Uptime**: > 99.9%

---

## 🎉 Production Ready Checklist

- [x] ML model loaded and verified
- [x] Database connected with indexes
- [x] Authentication system (JWT + bcrypt)
- [x] WebSocket real-time communication
- [x] GPS integration with routing
- [x] Smart hospital allocation
- [x] Enhanced AI insights
- [x] Analytics dashboard
- [x] Mobile-responsive UI
- [x] Error handling and logging
- [x] Security configurations
- [x] API documentation
- [x] Testing suite
- [x] Deployment scripts

---

## 📚 API Documentation

Full API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

**System Status**: ✅ PRODUCTION READY
**Version**: 0.2.0
**Last Updated**: 2024-04-13
