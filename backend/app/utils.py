# backend/app/utils.py
from pathlib import Path
import joblib
from loguru import logger as log

# ------------------------------------------------------------------
# Load the persisted pipeline + mappings (lazy, singleton)
_MODEL = None
_LABEL_MAP = None
_FEATURE_IMP = None

def load_artifacts():
    global _MODEL, _LABEL_MAP, _FEATURE_IMP
    if _MODEL is None:
        model_path = Path(__file__).parent.parent / "models" / "triage_model.pkl"
        label_path = Path(__file__).parent.parent / "models" / "label_map.pkl"
        imp_path   = Path(__file__).parent.parent / "models" / "feature_importance.pkl"
        
        _MODEL = joblib.load(model_path)
        _LABEL_MAP = joblib.load(label_path)
        _FEATURE_IMP = joblib.load(imp_path)
        log.info("Model, label map and feature importance loaded.")
    
    return _MODEL, _LABEL_MAP, _FEATURE_IMP

# ------------------------------------------------------------------
# Severity → colour mapping used by UI (also sent back if you want)
SEVERITY_COLORS = {
    "Immediate": "#ff4d4d",  # red
    "Urgent": "#ff9500",      # orange
    "Moderate": "#ffd200",   # yellow
    "Minor": "#4caf50",       # green
}

def severity_code_to_name(code: int) -> str:
    """Translate integer label (0‑3) to human‑readable name."""
    # 0 = Immediate, 1 = Urgent, 2 = Moderate, 3 = Minor
    return {0: "Immediate", 1: "Urgent", 2: "Moderate", 3: "Minor"}[code]

def get_color(severity_name: str) -> str:
    return SEVERITY_COLORS.get(severity_name, "#777777")
