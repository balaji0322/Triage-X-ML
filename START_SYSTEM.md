# 🚀 TRIAGE-X QUICK START GUIDE

## Prerequisites Check

✅ Python 3.10+ installed
✅ Node.js 18+ installed  
✅ MongoDB running on localhost:27017

## Step 1: Start MongoDB

### Windows
```bash
net start MongoDB
```

### Mac/Linux
```bash
brew services start mongodb-community
# OR
sudo systemctl start mongodb
```

Verify MongoDB is running:
```bash
mongosh --eval "db.version()"
```

## Step 2: Start Backend (Terminal 1)

```bash
cd backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the API server
python run_server.py
```

**Backend will be available at:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

## Step 3: Start Frontend (Terminal 2)

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start the React app
npm start
```

**Frontend will open at:** http://localhost:3000

## Step 4: Verify System

Open a third terminal and run:

```bash
# Verify all components
python backend/verify_system.py

# Run integration tests
python backend/test_integration.py
```

## Step 5: Use the System

### Create Ambulance Account
1. Go to http://localhost:3000/ambulance/signup
2. Enter:
   - Driver Name: `John Doe`
   - Ambulance Number: `AMB-001`
   - Password: `password123`
3. Click "Sign Up"

### Create Hospital Account
1. Go to http://localhost:3000/hospital/signup
2. Enter:
   - Hospital Name: `City General Hospital`
   - Address: `123 Main St, New York`
   - Password: `hospital123`
3. **SAVE THE HOSPITAL ID** shown on screen!
4. Click "Sign Up"

### Test Ambulance Dashboard
1. Login as ambulance
2. Enter patient data (use realistic values)
3. Click "Predict Severity"
4. Review the prediction
5. Click "Send Case to Hospital"

### Test Hospital Dashboard
1. Login as hospital (use saved Hospital ID)
2. View incoming cases
3. Check severity statistics
4. Filter by severity level
5. Dashboard auto-refreshes every 10 seconds

## Troubleshooting

### MongoDB Not Running
```bash
# Windows
net start MongoDB

# Mac
brew services start mongodb-community

# Linux
sudo systemctl start mongodb
```

### Port Already in Use

**Backend (Port 8000):**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

**Frontend (Port 3000):**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:3000 | xargs kill -9
```

### Backend Errors

Check if model files exist:
```bash
ls backend/models/
# Should see: triage_model.pkl, label_map.pkl, feature_importance.pkl
```

If missing, generate data and train model:
```bash
cd backend
python data/generate_data.py
python app/train_model.py
```

### Frontend Errors

Clear cache and reinstall:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│                  http://localhost:3000                   │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Login Page   │  │  Ambulance   │  │   Hospital   │ │
│  │              │  │  Dashboard   │  │  Dashboard   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTP/REST + JWT
┌────────────────────────▼─────────────────────────────────┐
│                   BACKEND (FastAPI)                      │
│                 http://localhost:8000                    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Auth Routes  │  │  ML Model    │  │  Database    │ │
│  │ (JWT/Bcrypt) │  │  (XGBoost)   │  │  (MongoDB)   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## API Endpoints

### Public
- `POST /predict` - ML prediction
- `GET /ping` - Health check
- `POST /api/ambulance/signup` - Register ambulance
- `POST /api/ambulance/login` - Ambulance login
- `POST /api/hospital/signup` - Register hospital
- `POST /api/hospital/login` - Hospital login

### Protected (Ambulance)
- `POST /api/send-case` - Submit case
- `GET /api/ambulance/recent-cases` - Get recent cases

### Protected (Hospital)
- `GET /api/cases` - Get all cases
- `GET /api/hospital/stats` - Get statistics

## Next Steps

1. ✅ System is running
2. ✅ Create test accounts
3. ✅ Submit test cases
4. ✅ View cases in hospital dashboard
5. 📝 Customize for your needs
6. 🚀 Deploy to production

## Production Deployment

Before deploying to production:

1. Change `SECRET_KEY` in `backend/app/auth.py`
2. Use environment variables for secrets
3. Configure CORS for specific domains
4. Use MongoDB Atlas or managed database
5. Enable HTTPS
6. Set up proper logging
7. Add rate limiting
8. Configure monitoring

## Support

For issues or questions:
- Check `SYSTEM_ARCHITECTURE.md` for detailed architecture
- Review `AUTH_SYSTEM_README.md` for authentication details
- See `BACKEND_VERIFICATION.md` for test results

---

**Built with ❤️ using Python, FastAPI, React, and XGBoost**
