# 🔐 TRIAGE-X Authentication System

## 📖 Overview

Complete authentication and authorization system built around the existing ML triage model. Features role-based access control, JWT authentication, and real-time dashboards for Ambulance and Hospital users.

---

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: REST API framework
- **MongoDB**: NoSQL database for users and cases
- **JWT**: Token-based authentication
- **Bcrypt**: Password hashing
- **XGBoost**: Existing ML model (unchanged)

### Frontend Stack
- **React**: UI framework
- **React Router**: Client-side routing
- **Axios**: HTTP client with interceptors
- **CSS3**: Custom styling with responsive design

---

## 🔑 Authentication Flow

### Ambulance Registration
```
User → Signup Form → Backend validates → Hash password → 
Store in MongoDB → Generate JWT → Return token + user data → 
Store in localStorage → Redirect to dashboard
```

### Hospital Registration
```
User → Signup Form → Backend validates → Generate Hospital ID → 
Hash password → Store in MongoDB → Generate JWT → 
Display Hospital ID (3 seconds) → Redirect to dashboard
```

### Login Flow
```
User → Login Form → Backend validates credentials → 
Verify password hash → Generate JWT → Return token → 
Store in localStorage → Redirect to role-specific dashboard
```

### Protected Routes
```
Request → Axios interceptor adds JWT → Backend verifies token → 
Check role permissions → Allow/Deny access
```

---

## 🗄️ Database Schema

### Ambulances Collection
```javascript
{
  _id: "uuid",
  driver_name: "John Doe",
  ambulance_number: "AMB-001",  // UNIQUE
  password_hash: "bcrypt_hash",
  created_at: "2024-01-01T00:00:00Z"
}
```

### Hospitals Collection
```javascript
{
  hospital_id: "HOSP-NEW-1234",  // UNIQUE, auto-generated
  hospital_name: "City General Hospital",
  address: "123 Main St, New York",
  password_hash: "bcrypt_hash",
  created_at: "2024-01-01T00:00:00Z"
}
```

### Cases Collection
```javascript
{
  case_id: "uuid",
  ambulance_number: "AMB-001",
  driver_name: "John Doe",
  patient_data: {
    heart_rate: 110,
    systolic_bp: 140,
    diastolic_bp: 90,
    oxygen_saturation: 92,
    temperature: 38.5,
    respiratory_rate: 24,
    age: 65,
    gender: "male",
    chest_pain: 1,
    fever: 1,
    // ... other features
  },
  severity: "Urgent",
  confidence: 0.87,
  timestamp: "2024-01-01T12:00:00Z",
  status: "pending"
}
```

---

## 🛣️ API Routes

### Public Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ambulance/signup` | Register ambulance |
| POST | `/api/ambulance/login` | Ambulance login |
| POST | `/api/hospital/signup` | Register hospital |
| POST | `/api/hospital/login` | Hospital login |
| POST | `/predict` | ML prediction (existing) |
| GET | `/ping` | Health check |

### Protected Routes (Ambulance)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/send-case` | Submit case | Bearer token |
| GET | `/api/ambulance/recent-cases` | Get recent cases | Bearer token |

### Protected Routes (Hospital)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/cases` | Get all cases | Bearer token |
| GET | `/api/hospital/stats` | Get severity stats | Bearer token |

---

## 🎨 Frontend Routes

| Path | Component | Access |
|------|-----------|--------|
| `/` | Redirect to `/login` | Public |
| `/login` | LoginPage | Public |
| `/ambulance/signup` | AmbulanceSignup | Public |
| `/hospital/signup` | HospitalSignup | Public |
| `/ambulance/dashboard` | AmbulanceDashboard | Ambulance only |
| `/hospital/dashboard` | HospitalDashboard | Hospital only |

---

## 🔒 Security Features

### Password Security
- Bcrypt hashing with automatic salt generation
- Minimum 6 characters required
- Password confirmation on signup
- Never stored in plain text

### JWT Tokens
- 24-hour expiration
- Includes user ID and role
- Signed with SECRET_KEY
- Verified on every protected request

### Role-Based Access Control (RBAC)
- Ambulance role: Can submit cases, view own cases
- Hospital role: Can view all cases, see statistics
- Middleware enforces role requirements
- Automatic logout on unauthorized access

### API Security
- CORS configured for specific origins
- Request validation with Pydantic
- Error messages don't leak sensitive info
- MongoDB injection prevention

---

## 🚑 Ambulance Dashboard Features

### Patient Input Form
- Vitals: HR, BP, SpO2, Temperature, Respiratory Rate
- Demographics: Age, Gender
- Symptoms: Chest Pain, Fever, Breathing Difficulty, Injury
- Medical History: Diabetes, Heart Disease, Hypertension, Asthma

### Prediction Display
- Color-coded severity (Red/Orange/Yellow/Green)
- Confidence percentage
- Send to hospital button

### Recent Cases
- Last 5 submitted cases
- Quick view of severity and vitals
- Timestamp for each case

---

## 🏥 Hospital Dashboard Features

### Statistics Cards
- Immediate cases count (Red)
- Urgent cases count (Orange)
- Moderate cases count (Yellow)
- Minor cases count (Green)
- Total cases count

### Case Filtering
- View all cases
- Filter by severity level
- One-click filtering

### Live Cases Table
- Real-time case list
- Ambulance details
- Patient vitals
- Severity with color coding
- Confidence scores
- Auto-refresh every 10 seconds

### Critical Case Highlighting
- Immediate cases highlighted in red background
- Easy identification of urgent patients

---

## 🎨 UI/UX Design

### Color Scheme
- Primary: Purple gradient (#667eea to #764ba2)
- Immediate: Red (#ef4444)
- Urgent: Orange (#f97316)
- Moderate: Yellow (#eab308)
- Minor: Green (#22c55e)

### Responsive Design
- Mobile-friendly layouts
- Grid-based responsive components
- Touch-friendly buttons
- Readable on all screen sizes

### User Experience
- Clear error messages
- Loading states
- Success notifications
- Auto-redirect after actions
- Persistent login (localStorage)

---

## 🧠 ML Integration

### Prediction Endpoint
```javascript
POST /predict
{
  heart_rate: 110,
  systolic_bp: 140,
  // ... all features
}

Response:
{
  severity: "Urgent",
  severity_code: 1,
  confidence: 0.87
}
```

### Model Loading
- Loads existing `triage_model.pkl` on startup
- No modifications to ML pipeline
- Uses original feature set
- Returns same severity labels

### Feature Compatibility
- All 15 input features preserved
- Same preprocessing pipeline
- Compatible with existing model
- No retraining required

---

## 📊 Data Flow

### Case Submission Flow
```
Ambulance enters data → Predict severity → Display result → 
Send case → Store in MongoDB → Hospital sees case → 
Auto-refresh updates list
```

### Authentication Flow
```
User credentials → Backend validation → JWT generation → 
Frontend storage → Axios interceptor → Protected requests → 
Token verification → Access granted
```

---

## 🔧 Configuration

### Backend Configuration
File: `backend/app/database.py`
```python
MONGO_URL = "mongodb://localhost:27017/"
DB_NAME = "triage_system"
```

File: `backend/app/auth.py`
```python
SECRET_KEY = "your-secret-key"  # Change in production!
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
```

### Frontend Configuration
File: `frontend/.env`
```env
REACT_APP_API_URL=http://localhost:8000
```

---

## 🧪 Testing

### Manual Testing Checklist

**Ambulance Tests:**
- [ ] Signup with valid data
- [ ] Signup with duplicate ambulance number (should fail)
- [ ] Login with correct credentials
- [ ] Login with wrong password (should fail)
- [ ] Submit patient data and get prediction
- [ ] Send case to hospital
- [ ] View recent cases
- [ ] Logout and verify redirect

**Hospital Tests:**
- [ ] Signup and receive hospital ID
- [ ] Login with hospital ID
- [ ] View all cases
- [ ] Filter cases by severity
- [ ] Verify statistics are correct
- [ ] Check auto-refresh works
- [ ] Verify critical cases highlighted
- [ ] Logout and verify redirect

**Security Tests:**
- [ ] Access protected route without token (should redirect)
- [ ] Access ambulance route as hospital (should fail)
- [ ] Access hospital route as ambulance (should fail)
- [ ] Token expiration handling

---

## 🚀 Deployment Considerations

### Production Checklist
- [ ] Change SECRET_KEY to strong random value
- [ ] Use environment variables for all secrets
- [ ] Configure CORS for specific domains
- [ ] Use MongoDB Atlas or managed database
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure rate limiting
- [ ] Add request validation
- [ ] Set up monitoring
- [ ] Create backup strategy

### Environment Variables
```bash
# Backend
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/
SECRET_KEY=<generate-strong-key>
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
REACT_APP_API_URL=https://api.yourdomain.com
```

---

## 📈 Future Enhancements

### Potential Features
- Email verification
- Password reset functionality
- Two-factor authentication
- Case status updates (pending/in-progress/completed)
- Real-time WebSocket updates
- Case assignment to specific hospitals
- Ambulance location tracking
- Patient history lookup
- Export cases to PDF/CSV
- Advanced analytics dashboard
- Mobile app (React Native)

---

## 🐛 Common Issues & Solutions

### Issue: MongoDB Connection Failed
**Solution:** Ensure MongoDB is running
```bash
# Check status
sudo systemctl status mongodb

# Start service
sudo systemctl start mongodb
```

### Issue: JWT Token Invalid
**Solution:** Clear localStorage and login again
```javascript
localStorage.clear()
```

### Issue: CORS Error
**Solution:** Check backend CORS configuration in `main.py`
```python
allow_origins=["http://localhost:3000"]
```

### Issue: Hospital ID Not Showing
**Solution:** Check browser console for errors, verify backend logs

---

## 📚 Code Structure

### Backend Files
```
backend/app/
├── main.py              # FastAPI app, startup, CORS
├── auth.py              # JWT, password hashing, dependencies
├── auth_routes.py       # All auth & case endpoints
├── auth_schemas.py      # Pydantic models for auth
├── database.py          # MongoDB connection & setup
├── model.py             # ML model loading (EXISTING)
├── schemas.py           # ML prediction schemas (EXISTING)
└── utils.py             # Helper functions (EXISTING)
```

### Frontend Files
```
frontend/src/
├── pages/
│   ├── LoginPage.jsx           # Split login (ambulance/hospital)
│   ├── AmbulanceSignup.jsx     # Ambulance registration
│   ├── HospitalSignup.jsx      # Hospital registration
│   ├── AmbulanceDashboard.jsx  # Ambulance dashboard
│   └── HospitalDashboard.jsx   # Hospital dashboard
├── App.js               # Router configuration
└── api.js               # API calls with auth interceptors
```

---

## 🎓 Learning Resources

### Technologies Used
- FastAPI: https://fastapi.tiangolo.com/
- MongoDB: https://docs.mongodb.com/
- JWT: https://jwt.io/introduction
- React Router: https://reactrouter.com/
- Axios: https://axios-http.com/

---

## ✅ Summary

This authentication system provides:
- ✅ Secure user registration and login
- ✅ Role-based access control
- ✅ JWT token authentication
- ✅ MongoDB data persistence
- ✅ Real-time dashboards
- ✅ ML model integration (unchanged)
- ✅ Responsive UI design
- ✅ Production-ready architecture

**The ML model remains completely untouched - only loading and using existing .pkl files for predictions.**

---

**Built with ❤️ for emergency medical triage**
