"""
Model training, loading, and inference helpers for triage prediction.
"""
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "triage_model.pkl"

# Feature columns (must match generate_data.py output)
NUMERIC_FEATURES = [
    "heart_rate",
    "systolic_bp",
    "diastolic_bp",
    "oxygen_saturation",
    "temperature",
    "respiratory_rate",
    "age",
]

BINARY_FEATURES = [
    "chest_pain",
    "fever",
    "breathing_difficulty",
    "injury_type",
    "diabetes",
    "heart_disease",
    "hypertension",
    "asthma",
]

CATEGORICAL_FEATURES = ["gender"]

TARGET = "severity"


def train_model(data_path: Path = DATA_DIR / "triage_dataset.csv"):
    """
    Train XGBoost classifier on triage dataset and save pipeline.
    """
    print(f"📂 Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Separate features and target
    X = df.drop(columns=[TARGET])
    y = df[TARGET]
    
    print(f"📊 Dataset shape: {X.shape}, Classes: {y.unique()}")
    print(f"   Class distribution:\n{y.value_counts().sort_index()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Build preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("bin", "passthrough", BINARY_FEATURES),
            ("cat", LabelEncoder() if len(CATEGORICAL_FEATURES) > 0 else "passthrough", CATEGORICAL_FEATURES),
        ],
        remainder="drop"
    )
    
    # XGBoost classifier
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric="mlogloss",
        use_label_encoder=False,
    )
    
    # Full pipeline
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", model),
    ])
    
    print("🔧 Training model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✅ Model trained successfully!")
    print(f"   Test Accuracy: {accuracy:.3f}")
    print(f"\n📈 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Immediate", "Urgent", "Moderate", "Minor"]))
    
    print(f"\n🔀 Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Cross-validation score
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring="accuracy")
    print(f"\n🎯 Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    
    # Save model
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"\n💾 Model saved to {MODEL_PATH}")
    
    return pipeline


def load_model(model_path: Path = MODEL_PATH):
    """
    Load trained model pipeline from disk.
    """
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. "
            f"Please run train_model() first or generate data and train."
        )
    
    pipeline = joblib.load(model_path)
    print(f"✅ Model loaded from {model_path}")
    return pipeline


def predict_triage(pipeline, patient_data: dict) -> dict:
    """
    Predict triage severity for a single patient.
    
    Args:
        pipeline: Trained sklearn pipeline
        patient_data: Dict with patient features
    
    Returns:
        Dict with prediction and probabilities
    """
    # Convert to DataFrame (pipeline expects this format)
    df = pd.DataFrame([patient_data])
    
    # Ensure all required columns exist
    all_features = NUMERIC_FEATURES + BINARY_FEATURES + CATEGORICAL_FEATURES
    for col in all_features:
        if col not in df.columns:
            df[col] = 0  # Default value for missing features
    
    # Predict
    prediction = pipeline.predict(df)[0]
    probabilities = pipeline.predict_proba(df)[0]
    
    # Map to labels
    severity_map = {
        0: "Immediate",
        1: "Urgent",
        2: "Moderate",
        3: "Minor"
    }
    
    return {
        "severity": severity_map[prediction],
        "severity_code": int(prediction),
        "confidence": float(probabilities[prediction]),
        "probabilities": {
            severity_map[i]: float(prob) 
            for i, prob in enumerate(probabilities)
        }
    }


if __name__ == "__main__":
    # Generate data if it doesn't exist
    data_file = DATA_DIR / "triage_dataset.csv"
    if not data_file.exists():
        print("⚠️  Dataset not found. Generating synthetic data...")
        import sys
        sys.path.append(str(DATA_DIR))
        from generate_data import main as generate_data
        generate_data()
    
    # Train model
    train_model()
    
    # Test prediction
    print("\n🧪 Testing prediction...")
    pipeline = load_model()
    
    test_patient = {
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
    }
    
    result = predict_triage(pipeline, test_patient)
    print(f"\n🏥 Test Patient Prediction:")
    print(f"   Severity: {result['severity']} (confidence: {result['confidence']:.2%})")
    print(f"   All probabilities: {result['probabilities']}")
