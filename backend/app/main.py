# backend/app/main.py
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from loguru import logger as log
import pandas as pd
import numpy as np

from .schemas import PatientInput, PredictionResponse
from .utils import load_artifacts, severity_code_to_name, get_color

app = FastAPI(
    title="TRIAGE‑X API",
    description="Predict patient severity from vitals, symptoms, history and demographics.",
    version="0.1.0",
)

# ------------------------------------------------------------------
# CORS (so the React UI can call the API locally)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production (specific domains)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    log.info("🚀 TRIAGE‑X service starting...")
    try:
        load_artifacts()
        log.info("✅ Model artifacts loaded successfully")
        log.info("🚀 TRIAGE‑X service ready")
    except Exception as e:
        log.error(f"❌ Failed to load model artifacts: {e}")
        raise

@app.on_event("shutdown")
def shutdown_event():
    log.info("🛑 TRIAGE‑X service shutting down")

# ------------------------------------------------------------------
@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PatientInput):
    """Predict patient triage severity."""
    log.debug(f"📥 Received prediction request")
    
    # Convert Pydantic model to DataFrame (single‑row)
    try:
        X = json.loads(payload.json())
        log.debug(f"Patient data: age={X.get('age')}, HR={X.get('heart_rate')}, O2={X.get('oxygen_saturation')}")
    except Exception as exc:
        log.error(f"❌ Invalid payload: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    
    try:
        # 1️⃣  Load model & label map
        model, label_map, _ = load_artifacts()
        
        # 2️⃣  Predict
        df = pd.DataFrame([X])
        probs = model.predict_proba(df)[0]
        pred_index = int(probs.argmax())
        pred_name = label_map[str(pred_index)]
        confidence = float(probs[pred_index])
        
        log.info(f"✅ Inference: predicted {pred_name} (code {pred_index}) with confidence {confidence:.4f}")
        
        # 3️⃣  Build response
        response = PredictionResponse(
            severity=pred_name,
            severity_code=pred_index,
            confidence=round(confidence, 4)
        )
        
        return response
        
    except Exception as e:
        log.error(f"❌ Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# ------------------------------------------------------------------
# Optional: expose feature importance (global) for UI / debugging
@app.get("/feature_importance")
def feature_importance():
    """Get global feature importance from the trained model."""
    log.debug("📊 Feature importance requested")
    try:
        _, _, fi = load_artifacts()
        # Return sorted list of (feature, importance)
        import operator
        sorted_fi = sorted(fi.items(), key=operator.itemgetter(1), reverse=True)
        log.info(f"✅ Returned {len(sorted_fi)} feature importance scores")
        return JSONResponse(content={"importance": sorted_fi})
    except Exception as e:
        log.error(f"❌ Failed to get feature importance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------
# Local explanation (SHAP) – optional endpoint
@app.post("/explain")
def explain(payload: PatientInput):
    """
    Get SHAP values for a specific prediction.
    Returns feature importance for the predicted class.
    """
    log.debug("🔍 SHAP explanation requested")
    
    try:
        from shap import TreeExplainer
    except ImportError:
        log.error("❌ SHAP not installed")
        raise HTTPException(
            status_code=501,
            detail="SHAP not installed. Run: pip install shap"
        )
    
    try:
        # Load model
        model, label_map, _ = load_artifacts()
        
        # Convert to DataFrame
        X = json.loads(payload.json())
        df = pd.DataFrame([X])
        
        # Get prediction
        pred_index = model.predict(df)[0]
        pred_name = label_map[str(pred_index)]
        
        log.debug(f"Computing SHAP values for {pred_name} prediction")
        
        # Create SHAP explainer for the XGBoost model
        explainer = TreeExplainer(model.named_steps["model"])
        
        # Transform data through preprocessing pipeline
        X_transformed = model.named_steps["preprocess"].transform(df)
        
        # Get SHAP values (multi-class array)
        shap_vals = explainer.shap_values(X_transformed)
        
        # Extract SHAP values for the predicted class
        class_shap = shap_vals[pred_index][0].tolist()
        
        # Get feature names after preprocessing
        feature_names = model.named_steps["preprocess"].get_feature_names_out().tolist()
        
        # Create feature importance dictionary
        feature_importance = dict(zip(feature_names, class_shap))
        
        # Sort by absolute importance
        sorted_importance = sorted(
            feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        log.info(f"✅ SHAP explanation generated for {pred_name} prediction ({len(sorted_importance)} features)")
        
        return JSONResponse(content={
            "predicted_class": pred_name,
            "predicted_code": int(pred_index),
            "feature_importance": dict(sorted_importance),
            "base_value": float(explainer.expected_value[pred_index])
        })
        
    except Exception as e:
        log.error(f"❌ SHAP explanation failed: {e}")
        raise HTTPException(status_code=500, detail=f"SHAP error: {str(e)}")

# ------------------------------------------------------------------
# Health check
@app.get("/ping")
def ping():
    """Health check endpoint."""
    log.debug("🏓 Ping received")
    return {"msg": "pong", "status": "healthy"}
