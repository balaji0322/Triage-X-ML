# backend/data/generate_data.py
import numpy as np
import pandas as pd
import json
from pathlib import Path

RNG = np.random.default_rng(seed=42)

def _sample_vitals(n):
    """Generate realistic vital signs."""
    # Heart rate (bpm)
    hr = RNG.normal(loc=80, scale=15, size=n).clip(40, 180)
    # Systolic / Diastolic BP (mmHg)
    sbp = RNG.normal(loc=120, scale=20, size=n).clip(80, 200)
    dbp = RNG.normal(loc=80, scale=12, size=n).clip(50, 130)
    # Oxygen saturation (%)
    spo2 = RNG.normal(loc=97, scale=2, size=n).clip(80, 100)
    # Temperature (°C)
    temp = RNG.normal(loc=37, scale=0.8, size=n).clip(35, 41)
    # Respiratory rate (breaths/min)
    rr = RNG.normal(loc=16, scale=4, size=n).clip(8, 40)
    
    return pd.DataFrame({
        "heart_rate": hr,
        "systolic_bp": sbp,
        "diastolic_bp": dbp,
        "oxygen_saturation": spo2,
        "temperature": temp,
        "respiratory_rate": rr,
    })

def _sample_binary(name, n, prob=0.2):
    """Return a DataFrame with a single binary column."""
    return pd.DataFrame({name: RNG.binomial(1, prob, size=n)})

def _sample_symptoms(n):
    """Symptoms are binary, different prevalence per symptom."""
    return pd.concat([
        _sample_binary("chest_pain",      n, prob=0.15),
        _sample_binary("fever",           n, prob=0.30),
        _sample_binary("breathing_difficulty", n, prob=0.10),
        _sample_binary("injury_type",    n, prob=0.05),   # 1 = traumatic injury
    ], axis=1)

def _sample_history(n):
    return pd.concat([
        _sample_binary("diabetes",     n, prob=0.12),
        _sample_binary("heart_disease",n, prob=0.10),
        _sample_binary("hypertension",n, prob=0.18),
        _sample_binary("asthma",       n, prob=0.09),
    ], axis=1)

def _sample_demographics(n):
    age = RNG.integers(0, 100, size=n)                 # years
    gender = RNG.choice(["male", "female", "other"], size=n, p=[0.48, 0.48, 0.04])
    return pd.DataFrame({
        "age": age,
        "gender": gender,
    })

def _rule_based_label(df):
    """Very simple triage logic → severity (0=Immediate,1=Urgent,2=Moderate,3=Minor)."""
    # start with a score of 0, increase with bad signs
    score = np.zeros(len(df))
    
    # Vital‐sign thresholds (rough clinical cut‑offs)
    score += (df["heart_rate"] > 120).astype(int) * 2
    score += (df["systolic_bp"] < 90).astype(int) * 2
    score += (df["oxygen_saturation"] < 90).astype(int) * 3
    score += (df["temperature"] > 38.5).astype(int) * 1
    score += (df["respiratory_rate"] > 24).astype(int) * 2
    
    # Symptoms
    score += df["chest_pain"] * 2
    score += df["breathing_difficulty"] * 3
    score += df["injury_type"] * 2
    
    # History (adds risk)
    score += df["heart_disease"] * 1
    score += df["hypertension"] * 1
    
    # Age factor (elderly more vulnerable)
    score += (df["age"] > 70).astype(int) * 1
    
    # Map final numeric score to severity buckets
    # 0‑2 → Minor, 3‑5 → Moderate, 6‑8 → Urgent, 9+ → Immediate
    severity = pd.cut(
        score,
        bins=[-np.inf, 2, 5, 8, np.inf],
        labels=[3, 2, 1, 0]   # 0 = Immediate, 1 = Urgent, …
    ).astype(int)
    
    return severity

def main(samples: int = 2000, out_path: Path = Path(__file__).parent / "triage_dataset.csv"):
    # Assemble all columns
    df = pd.concat([
        _sample_vitals(samples),
        _sample_symptoms(samples),
        _sample_history(samples),
        _sample_demographics(samples),
    ], axis=1)
    
    # Rule‑based label
    df["severity"] = _rule_based_label(df)
    
    # Shuffle rows
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Persist
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"✅ Synthetic dataset written to {out_path}")
    
    # Also write a tiny JSON with mapping for UI
    mapping = {
        "0": "Immediate",
        "1": "Urgent",
        "2": "Moderate",
        "3": "Minor"
    }
    (out_path.parent / "label_mapping.json").write_text(json.dumps(mapping, indent=2))

if __name__ == "__main__":
    main()
