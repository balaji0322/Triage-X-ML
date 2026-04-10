# 🏥 Triage-X - AI-Powered Patient Triage System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0.3-orange.svg)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent machine learning system for automated patient triage in emergency departments. Uses XGBoost classifier to predict patient severity levels based on vital signs, symptoms, and medical history.

## ✨ Features

- 🤖 **ML-Powered Predictions**: XGBoost model with 98% accuracy
- 🎯 **4 Severity Levels**: Immediate, Urgent, Moderate, Minor
- 📊 **Feature Importance**: Global and local (SHAP) explanations
- 🔔 **Smart Alerts**: Toast notifications for critical cases
- 🎨 **Modern UI**: Clean React interface with color-coded results
- 🐳 **Docker Ready**: Full containerization support
- 📝 **Comprehensive Logging**: Environment-aware logging system
- 🔒 **Input Validation**: Pydantic schemas with range checking

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional) Docker & Docker Compose

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/triage-x.git
cd triage-x
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate synthetic data
python data/generate_data.py

# Train model
python app/train_model.py

# Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start development server
npm start
```

Frontend will open at `http://localhost:3000`

### 4. Using Docker (Alternative)

```bash
# Build and start all services
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

## 📁 Project Structure

```
triage-x/
├── backend/                     # Python FastAPI + ML
│   ├── app/
│   │   ├── main.py              # FastAPI app with 4 endpoints
│   │   ├── model.py             # Model training pipeline
│   │   ├── train_model.py       # Training script
│   │   ├── schemas.py           # Pydantic models
│   │   ├── utils.py             # Helper functions
│   │   └── logger.py            # Logging configuration
│   ├── data/
│   │   ├── generate_data.py     # Synthetic data generator
│   │   └── triage_dataset.csv   # 2000 patient records
│   ├── models/
│   │   ├── triage_model.pkl     # Trained XGBoost pipeline
│   │   ├── label_map.pkl        # Severity mappings
│   │   └── feature_importance.pkl
│   ├── requirements.txt
│   ├── Dockerfile
│   └── test_backend_complete.py # Verification tests
│
├── frontend/                    # React UI
│   ├── src/
│   │   ├── App.js               # Main app component
│   │   ├── api.js               # API wrapper
│   │   └── components/
│   │       ├── PatientForm.jsx  # Input form
│   │       └── ResultCard.jsx   # Results display
│   ├── package.json
│   ├── Dockerfile
│   └── .env
│
├── docker-compose.yml           # Docker orchestration
├── .gitignore
└── README.md
```

## 🎯 API Endpoints

### POST /predict
Predict patient triage severity.

**Request**:
```json
{
  "heart_rate": 110,
  "systolic_bp": 115,
  "diastolic_bp": 75,
  "oxygen_saturation": 88,
  "temperature": 38.2,
  "respiratory_rate": 28,
  "chest_pain": 1,
  "fever": 1,
  "breathing_difficulty": 1,
  "injury_type": 0,
  "diabetes": 0,
  "heart_disease": 1,
  "hypertension": 0,
  "asthma": 0,
  "age": 68,
  "gender": "male"
}
```

**Response**:
```json
{
  "severity": "Urgent",
  "severity_code": 1,
  "confidence": 0.9234
}
```

### GET /feature_importance
Get global feature importance scores.

### POST /explain
Get SHAP explanation for a specific prediction.

### GET /ping
Health check endpoint.

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run comprehensive verification
python test_backend_complete.py

# Test specific endpoint
python test_api.py

# Test SHAP explanations
python test_shap.py
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📊 Model Details

- **Algorithm**: XGBoost Classifier
- **Accuracy**: ~98%
- **Classes**: 3 (Urgent, Moderate, Minor)
- **Features**: 17 input features + 1 derived
- **Training Data**: 2000 synthetic patient records
- **Preprocessing**: StandardScaler + OneHotEncoder

### Input Features

**Vitals** (6):
- Heart rate (30-250 bpm)
- Systolic BP (50-250 mmHg)
- Diastolic BP (30-150 mmHg)
- Oxygen saturation (50-100%)
- Temperature (30-45°C)
- Respiratory rate (5-60 breaths/min)

**Symptoms** (4):
- Chest pain (binary)
- Fever (binary)
- Breathing difficulty (binary)
- Injury type (binary)

**Medical History** (4):
- Diabetes (binary)
- Heart disease (binary)
- Hypertension (binary)
- Asthma (binary)

**Demographics** (3):
- Age (0-120 years)
- Gender (male/female/other)

## 📝 Documentation

- [Quick Start Guide](QUICK_START.md) - 6-step setup
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment
- [Docker Guide](DOCKER_GUIDE.md) - Container setup
- [Logging Guide](LOGGING_GUIDE.md) - Logging configuration
- [Explainability Guide](EXPLAINABILITY_GUIDE.md) - Model interpretability
- [Backend Verification](BACKEND_VERIFICATION.md) - Test results

## 🔧 Configuration

### Environment Variables

**Backend**:
```bash
ENVIRONMENT=development  # development, production, or testing
```

**Frontend** (`.env`):
```bash
REACT_APP_API_URL=http://localhost:8000
```

### Logging Modes

**Development** (default):
- Colorful console output
- DEBUG level
- Detailed format

**Production**:
```bash
export ENVIRONMENT=production
```
- File output with rotation
- INFO level
- 30-day retention
- Automatic compression

## 🐳 Docker Deployment

### Build Images

```bash
# Backend
docker build -t triage-backend ./backend

# Frontend
docker build -t triage-frontend ./frontend
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- XGBoost for the powerful ML framework
- FastAPI for the modern Python web framework
- React for the UI library
- SHAP for model explainability

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/yourusername/triage-x](https://github.com/yourusername/triage-x)

## ⚠️ Disclaimer

This is a demonstration project for educational purposes. It should not be used for actual medical triage without proper validation, regulatory approval, and clinical oversight.

---

**Built with ❤️ using Python, FastAPI, React, and XGBoost**
