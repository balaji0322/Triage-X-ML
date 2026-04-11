# 🚀 Quick Start Guide - TRIAGE-X Authentication System

## ⚡ Fast Setup (5 minutes)

### Step 1: Install MongoDB
```bash
# Windows: Download and install from
https://www.mongodb.com/try/download/community

# Mac (with Homebrew)
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Linux (Ubuntu)
sudo apt-get install mongodb
sudo systemctl start mongodb
```

### Step 2: Backend Setup
```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Start server
python run_server.py
```

**Backend running at: http://localhost:8000** ✅

### Step 3: Frontend Setup (New Terminal)
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start app
npm start
```

**Frontend running at: http://localhost:3000** ✅

---

## 🎯 Test the System

### 1. Create Ambulance Account
- Go to: http://localhost:3000/ambulance/signup
- Driver Name: `John Doe`
- Ambulance Number: `AMB-001`
- Password: `password123`
- Click "Sign Up"

### 2. Create Hospital Account
- Go to: http://localhost:3000/hospital/signup
- Hospital Name: `City General Hospital`
- Address: `123 Main St, New York`
- Password: `hospital123`
- **SAVE THE HOSPITAL ID** shown on screen!

### 3. Test Ambulance Dashboard
- Login as ambulance
- Enter sample patient data:
  - Heart Rate: 110
  - Systolic BP: 140
  - Diastolic BP: 90
  - SpO2: 92
  - Temperature: 38.5
  - Respiratory Rate: 24
  - Age: 65
  - Check: Chest Pain, Fever
- Click "Predict Severity"
- Click "Send Case to Hospital"

### 4. Test Hospital Dashboard
- Login as hospital (use saved Hospital ID)
- View incoming cases
- Check severity statistics
- Filter by severity level

---

## 🔍 Verify Everything Works

✅ Backend API: http://localhost:8000/docs  
✅ Health Check: http://localhost:8000/ping  
✅ Frontend: http://localhost:3000  
✅ MongoDB: Check connection in backend logs  

---

## 🐛 Quick Fixes

**MongoDB not running?**
```bash
# Windows
net start MongoDB

# Mac
brew services start mongodb-community

# Linux
sudo systemctl start mongodb
```

**Port already in use?**
```bash
# Kill process on port 8000 (backend)
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

**Frontend won't start?**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

---

## 📚 Next Steps

- Read full documentation: `SETUP_INSTRUCTIONS.md`
- Customize SECRET_KEY in `backend/app/auth.py`
- Configure MongoDB URL in `backend/app/database.py`
- Deploy to production

---

**You're all set! 🎉**
