# 🏥 TRIAGE-X Authentication System - Setup Instructions

## 📋 Overview
Complete authentication system with role-based dashboards for Ambulance and Hospital users, integrated with existing ML model.

## 🔧 Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (local or cloud)

---

## 🗄️ MongoDB Setup

### Option 1: Local MongoDB
1. Install MongoDB: https://www.mongodb.com/try/download/community
2. Start MongoDB service:
   ```bash
   # Windows
   net start MongoDB
   
   # Linux/Mac
   sudo systemctl start mongod
   ```

### Option 2: MongoDB Atlas (Cloud)
1. Create free account: https://www.mongodb.com/cloud/atlas
2. Create cluster and get connection string
3. Update `MONGO_URL` in `backend/app/database.py`

---

## 🔙 Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create virtual environment (if not exists)
```bash
python -m venv .venv
```

### 3. Activate virtual environment
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure environment (optional)
Create `.env` file in `backend/` directory:
```env
MONGO_URL=mongodb://localhost:27017/
SECRET_KEY=your-super-secret-key-change-this
```

### 6. Start backend server
```bash
python run_server.py
```

Backend will run on: **http://localhost:8000**

---

## 🎨 Frontend Setup

### 1. Navigate to frontend directory
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Configure API URL (optional)
Update `.env` file in `frontend/` directory:
```env
REACT_APP_API_URL=http://localhost:8000
```

### 4. Start frontend
```bash
npm start
```

Frontend will run on: **http://localhost:3000**

---

## 🚀 Usage Guide

### 🚑 Ambulance Flow

1. **Signup**: http://localhost:3000/ambulance/signup
   - Enter driver name
   - Enter unique ambulance number
   - Set password
   - Click "Sign Up"

2. **Login**: http://localhost:3000/login
   - Select "Ambulance" tab
   - Enter ambulance number and password
   - Click "Login"

3. **Dashboard Features**:
   - **Patient Input Form**: Enter vitals, symptoms, medical history
   - **Predict**: Click to get ML prediction (uses existing .pkl model)
   - **Send Case**: Submit case to hospital
   - **Recent Cases**: View last 5 submitted cases

### 🏥 Hospital Flow

1. **Signup**: http://localhost:3000/hospital/signup
   - Enter hospital name
   - Enter address
   - Set password
   - System auto-generates Hospital ID (format: HOSP-{CITY}-{4DIGIT})
   - **SAVE YOUR HOSPITAL ID** - needed for login

2. **Login**: http://localhost:3000/login
   - Select "Hospital" tab
   - Enter hospital ID and password
   - Click "Login"

3. **Dashboard Features**:
   - **Severity Stats**: Real-time counts by severity level
   - **Filter Cases**: View all or filter by severity
   - **Live Cases Table**: All incoming cases with vitals
   - **Auto-refresh**: Updates every 10 seconds
   - **Critical Highlighting**: Immediate cases highlighted in red

---

## 🔐 Authentication Details

### Roles
- **Ambulance**: Can submit cases, view own recent cases
- **Hospital**: Can view all cases, see statistics

### Security Features
- Passwords hashed with bcrypt
- JWT tokens (24-hour expiry)
- Role-based access control
- Auto-logout on token expiry

### Database Collections
- `ambulances`: Driver info, ambulance number, password hash
- `hospitals`: Hospital info, auto-generated ID, password hash
- `cases`: Patient data, severity, confidence, timestamps

---

## 🧠 ML Model Integration

**IMPORTANT**: The system uses the EXISTING ML model at `backend/models/triage_model.pkl`

### Model Files (DO NOT MODIFY)
- `triage_model.pkl` - Trained XGBoost model
- `label_map.pkl` - Severity label mapping
- `feature_importance.pkl` - Feature importance data

### Prediction Flow
1. Ambulance enters patient data
2. Frontend sends to `/predict` endpoint
3. Backend loads existing .pkl model
4. Model returns severity + confidence
5. Ambulance can send case to hospital

---

## 📊 API Endpoints

### Authentication
- `POST /api/ambulance/signup` - Register ambulance
- `POST /api/ambulance/login` - Ambulance login
- `POST /api/hospital/signup` - Register hospital
- `POST /api/hospital/login` - Hospital login

### Cases (Protected)
- `POST /api/send-case` - Send case (ambulance only)
- `GET /api/cases` - Get all cases (hospital only)
- `GET /api/ambulance/recent-cases` - Get recent cases (ambulance only)
- `GET /api/hospital/stats` - Get severity stats (hospital only)

### ML Prediction (Public)
- `POST /predict` - Get severity prediction
- `GET /feature_importance` - Get feature importance
- `POST /explain` - Get SHAP explanation

---

## 🎨 Color Coding

- **Immediate**: Red (#ef4444)
- **Urgent**: Orange (#f97316)
- **Moderate**: Yellow (#eab308)
- **Minor**: Green (#22c55e)

---

## 🐛 Troubleshooting

### Backend Issues
- **MongoDB connection failed**: Check if MongoDB is running
- **Model not found**: Ensure `backend/models/triage_model.pkl` exists
- **Import errors**: Reinstall dependencies with `pip install -r requirements.txt`

### Frontend Issues
- **API connection failed**: Check backend is running on port 8000
- **Login redirect loop**: Clear browser localStorage
- **Module not found**: Run `npm install` again

### Common Fixes
```bash
# Clear browser cache and localStorage
# In browser console:
localStorage.clear()

# Restart backend
cd backend
python run_server.py

# Restart frontend
cd frontend
npm start
```

---

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app with auth routes
│   │   ├── auth.py              # JWT & password hashing
│   │   ├── auth_routes.py       # Auth & case endpoints
│   │   ├── auth_schemas.py      # Pydantic models
│   │   ├── database.py          # MongoDB connection
│   │   ├── model.py             # ML model loading (EXISTING)
│   │   ├── schemas.py           # ML prediction schemas (EXISTING)
│   │   └── utils.py             # Helper functions (EXISTING)
│   ├── models/
│   │   ├── triage_model.pkl     # EXISTING ML MODEL
│   │   ├── label_map.pkl        # EXISTING
│   │   └── feature_importance.pkl # EXISTING
│   └── requirements.txt         # Updated with auth dependencies
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx           # Split login page
│   │   │   ├── AmbulanceSignup.jsx     # Ambulance registration
│   │   │   ├── HospitalSignup.jsx      # Hospital registration
│   │   │   ├── AmbulanceDashboard.jsx  # Ambulance dashboard
│   │   │   └── HospitalDashboard.jsx   # Hospital dashboard
│   │   ├── App.js               # Router setup
│   │   └── api.js               # API calls with auth
│   └── package.json             # Updated with react-router-dom
│
└── SETUP_INSTRUCTIONS.md        # This file
```

---

## ✅ Testing Checklist

### Ambulance
- [ ] Signup with unique ambulance number
- [ ] Login with credentials
- [ ] Enter patient data and predict
- [ ] View prediction result with color coding
- [ ] Send case to hospital
- [ ] View recent cases
- [ ] Logout

### Hospital
- [ ] Signup and receive hospital ID
- [ ] Login with hospital ID
- [ ] View severity statistics
- [ ] See all incoming cases
- [ ] Filter cases by severity
- [ ] Verify critical cases highlighted
- [ ] Auto-refresh working
- [ ] Logout

---

## 🎯 Key Features Implemented

✅ Two-role authentication (Ambulance & Hospital)  
✅ Unique ambulance number validation  
✅ Auto-generated hospital IDs (HOSP-{CITY}-{4DIGIT})  
✅ JWT token-based auth with bcrypt  
✅ Role-based dashboards  
✅ ML prediction using EXISTING .pkl model  
✅ Case submission and tracking  
✅ Real-time hospital dashboard  
✅ Severity color coding  
✅ Recent cases for ambulance  
✅ Statistics for hospital  
✅ Auto-refresh functionality  
✅ Responsive design  

---

## 📞 Support

For issues or questions:
1. Check MongoDB is running
2. Verify backend is on port 8000
3. Ensure frontend is on port 3000
4. Check browser console for errors
5. Review API logs in terminal

---

**Built with FastAPI, React, MongoDB, and XGBoost ML Model** 🚀
