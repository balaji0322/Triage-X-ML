# Triage-X Backend

FastAPI-based ML service for patient triage prediction using XGBoost.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Synthetic Data

```bash
cd data
python generate_data.py
```

This creates:
- `data/triage_dataset.csv` - 2000 synthetic patient records
- `data/label_mapping.json` - Severity level mapping

### 3. Train the Model

```bash
python -m app.train_model
```

This creates:
- `models/triage_model.pkl` - Trained XGBoost pipeline
- `models/label_map.pkl` - Label mapping for API
- `models/feature_importance.pkl` - Feature importance scores

Expected output:
- Test accuracy: ~98%
- Classes: Urgent, Moderate, Minor

### 4. Run the API

```bash
python -m app.main
```

Or with uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### POST /predict
Predict triage severity for a patient.

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
  "confidence": 87.5,
  "probabilities": {
    "Urgent": 87.5,
    "Moderate": 10.2,
    "Minor": 2.3
  },
  "priority": 1,
  "color": "#EA580C"
}
```

### GET /model/info
Get information about the loaded model.

**Response:**
```json
{
  "model_type": "XGBoost Classifier",
  "model_path": "models/triage_model.pkl",
  "label_mapping": {"0": "Urgent", "1": "Moderate", "2": "Minor"},
  "feature_importance": {...},
  "pipeline_steps": ["preprocess", "model"]
}
```

## Testing

Run the test script:
```bash
python test_api.py
```

Or use curl:
```bash
# Health check
curl http://localhost:8000/health

# Prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @test_patient.json
```

## Docker

Build and run with Docker:

```bash
# Build image
docker build -t triage-x-api .

# Run container
docker run -p 8000:8000 triage-x-api
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── model.py             # Model loading & inference
│   ├── train_model.py       # Enhanced training script
│   ├── schemas.py           # Pydantic models
│   ├── utils.py             # Helper functions
│   └── logger.py            # Logging configuration
├── data/
│   ├── generate_data.py     # Synthetic data generator
│   ├── triage_dataset.csv   # Generated dataset
│   └── label_mapping.json   # Severity labels
├── models/
│   ├── triage_model.pkl     # Trained model
│   ├── label_map.pkl        # Label mapping
│   └── feature_importance.pkl
├── requirements.txt
├── Dockerfile
└── test_api.py              # API test script
```

## Model Details

- **Algorithm**: XGBoost Classifier
- **Features**: 17 features (vitals, symptoms, history, demographics)
- **Classes**: 3 severity levels (Urgent, Moderate, Minor)
- **Preprocessing**: StandardScaler for numeric, OneHotEncoder for categorical
- **Performance**: ~98% accuracy on test set

## Development

Enable auto-reload during development:
```bash
uvicorn app.main:app --reload
```

View logs with color formatting thanks to loguru.
