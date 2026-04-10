"""Quick test of the complete backend."""
import pandas as pd
from app.utils import load_artifacts, get_color, severity_code_to_name

print("🧪 Quick Backend Test\n")

# Load artifacts
print("1. Loading model artifacts...")
try:
    model, label_map, feature_imp = load_artifacts()
    print(f"   ✅ Model loaded: {type(model)}")
    print(f"   ✅ Label map: {label_map}")
    print(f"   ✅ Feature importance: {len(feature_imp)} features")
except Exception as e:
    print(f"   ❌ Failed to load: {e}")
    exit(1)

# Test prediction
print("\n2. Testing prediction...")
test_patient = {
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

df = pd.DataFrame([test_patient])
prediction = model.predict(df)[0]
probabilities = model.predict_proba(df)[0]

severity = label_map[str(prediction)]
confidence = probabilities[prediction]
color = get_color(severity)

print(f"   Prediction: {prediction}")
print(f"   Severity: {severity}")
print(f"   Confidence: {confidence:.2%}")
print(f"   Color: {color}")

print("\n✅ Backend test completed successfully!")
