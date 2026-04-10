# backend/data/generate_data.py
import numpy as np
import pandas as pd
import json
from pathlib import Path

RNG = np.random.default_rng(seed=42)

def _sample_vitals(n, severity_bias=None):
    """Generate realistic vital signs with severity-based distributions."""
    if severity_bias is None:
        # Normal distribution
        hr = RNG.normal(loc=80, scale=15, size=n).clip(40, 180)
        sbp = RNG.normal(loc=120, scale=20, size=n).clip(80, 200)
        dbp = RNG.normal(loc=80, scale=12, size=n).clip(50, 130)
        spo2 = RNG.normal(loc=97, scale=2, size=n).clip(80, 100)
        temp = RNG.normal(loc=37, scale=0.8, size=n).clip(35, 41)
        rr = RNG.normal(loc=16, scale=4, size=n).clip(8, 40)
    else:
        # Severity-biased distributions
        if severity_bias == 'urgent':
            hr = RNG.normal(loc=110, scale=20, size=n).clip(90, 180)
            sbp = RNG.normal(loc=95, scale=15, size=n).clip(70, 140)
            dbp = RNG.normal(loc=65, scale=10, size=n).clip(40, 90)
            spo2 = RNG.normal(loc=88, scale=4, size=n).clip(75, 94)
            temp = RNG.normal(loc=38.5, scale=1.2, size=n).clip(36, 41)
            rr = RNG.normal(loc=26, scale=6, size=n).clip(20, 40)
        elif severity_bias == 'moderate':
            hr = RNG.normal(loc=90, scale=12, size=n).clip(70, 120)
            sbp = RNG.normal(loc=110, scale=15, size=n).clip(90, 150)
            dbp = RNG.normal(loc=75, scale=10, size=n).clip(60, 100)
            spo2 = RNG.normal(loc=94, scale=3, size=n).clip(88, 98)
            temp = RNG.normal(loc=37.8, scale=0.9, size=n).clip(36.5, 39.5)
            rr = RNG.normal(loc=20, scale=4, size=n).clip(14, 28)
        else:  # minor
            hr = RNG.normal(loc=75, scale=10, size=n).clip(60, 100)
            sbp = RNG.normal(loc=120, scale=12, size=n).clip(100, 140)
            dbp = RNG.normal(loc=80, scale=8, size=n).clip(65, 90)
            spo2 = RNG.normal(loc=98, scale=1.5, size=n).clip(95, 100)
            temp = RNG.normal(loc=37, scale=0.5, size=n).clip(36.2, 37.8)
            rr = RNG.normal(loc=16, scale=3, size=n).clip(12, 22)
    
    return pd.DataFrame({
        "heart_rate": hr.astype(int),
        "systolic_bp": sbp.astype(int),
        "diastolic_bp": dbp.astype(int),
        "oxygen_saturation": spo2.astype(int),
        "temperature": temp.round(1),
        "respiratory_rate": rr.astype(int),
    })

def _sample_binary(name, n, prob=0.2):
    """Return a DataFrame with a single binary column."""
    return pd.DataFrame({name: RNG.binomial(1, prob, size=n)})

def _sample_symptoms(n, severity_bias=None):
    """Symptoms with severity-based probabilities."""
    if severity_bias == 'urgent':
        chest_pain_prob = 0.45
        fever_prob = 0.60
        breathing_prob = 0.55
        injury_prob = 0.20
    elif severity_bias == 'moderate':
        chest_pain_prob = 0.20
        fever_prob = 0.40
        breathing_prob = 0.15
        injury_prob = 0.10
    else:  # minor
        chest_pain_prob = 0.05
        fever_prob = 0.15
        breathing_prob = 0.03
        injury_prob = 0.02
    
    return pd.concat([
        _sample_binary("chest_pain", n, prob=chest_pain_prob),
        _sample_binary("fever", n, prob=fever_prob),
        _sample_binary("breathing_difficulty", n, prob=breathing_prob),
        _sample_binary("injury_type", n, prob=injury_prob),
    ], axis=1)

def _sample_history(n, severity_bias=None):
    """Medical history with age-correlated probabilities."""
    if severity_bias == 'urgent':
        diabetes_prob = 0.25
        heart_prob = 0.30
        hypertension_prob = 0.35
        asthma_prob = 0.15
    elif severity_bias == 'moderate':
        diabetes_prob = 0.15
        heart_prob = 0.15
        hypertension_prob = 0.22
        asthma_prob = 0.12
    else:  # minor
        diabetes_prob = 0.08
        heart_prob = 0.05
        hypertension_prob = 0.12
        asthma_prob = 0.08
    
    return pd.concat([
        _sample_binary("diabetes", n, prob=diabetes_prob),
        _sample_binary("heart_disease", n, prob=heart_prob),
        _sample_binary("hypertension", n, prob=hypertension_prob),
        _sample_binary("asthma", n, prob=asthma_prob),
    ], axis=1)

def _sample_demographics(n, severity_bias=None):
    """Demographics with realistic age distributions."""
    if severity_bias == 'urgent':
        # Older population more likely to be urgent
        age = RNG.gamma(shape=8, scale=8, size=n).clip(18, 95).astype(int)
    elif severity_bias == 'moderate':
        age = RNG.gamma(shape=6, scale=7, size=n).clip(10, 85).astype(int)
    else:  # minor
        age = RNG.gamma(shape=4, scale=6, size=n).clip(5, 75).astype(int)
    
    gender = RNG.choice(["male", "female", "other"], size=n, p=[0.48, 0.48, 0.04])
    return pd.DataFrame({
        "age": age,
        "gender": gender,
    })

def generate_balanced_dataset(samples_per_class: dict):
    """Generate balanced dataset with specified samples per class."""
    dfs = []
    
    for severity, count in samples_per_class.items():
        if severity == 0:  # Urgent
            bias = 'urgent'
        elif severity == 1:  # Moderate
            bias = 'moderate'
        else:  # Minor
            bias = 'minor'
        
        df = pd.concat([
            _sample_vitals(count, severity_bias=bias),
            _sample_symptoms(count, severity_bias=bias),
            _sample_history(count, severity_bias=bias),
            _sample_demographics(count, severity_bias=bias),
        ], axis=1)
        
        df["severity"] = severity
        dfs.append(df)
    
    # Combine and shuffle
    df = pd.concat(dfs, ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return df

def add_feature_interactions(df):
    """Add derived features based on domain knowledge."""
    # Pulse pressure (indicator of cardiovascular health)
    df['pulse_pressure'] = df['systolic_bp'] - df['diastolic_bp']
    
    # Mean arterial pressure
    df['mean_arterial_pressure'] = df['diastolic_bp'] + (df['pulse_pressure'] / 3)
    
    # Shock index (HR / SBP) - higher values indicate shock
    df['shock_index'] = df['heart_rate'] / df['systolic_bp']
    
    # Age risk factor (elderly are more vulnerable)
    df['age_risk'] = (df['age'] > 65).astype(int)
    
    # Fever indicator
    df['has_fever'] = (df['temperature'] > 38.0).astype(int)
    
    # Hypoxia indicator
    df['hypoxia'] = (df['oxygen_saturation'] < 92).astype(int)
    
    # Tachycardia indicator
    df['tachycardia'] = (df['heart_rate'] > 100).astype(int)
    
    # Tachypnea indicator
    df['tachypnea'] = (df['respiratory_rate'] > 20).astype(int)
    
    # Hypotension indicator
    df['hypotension'] = (df['systolic_bp'] < 90).astype(int)
    
    # Comorbidity count
    df['comorbidity_count'] = (
        df['diabetes'] + df['heart_disease'] + 
        df['hypertension'] + df['asthma']
    )
    
    # Critical symptoms count
    df['critical_symptoms'] = (
        df['chest_pain'] + df['breathing_difficulty'] + 
        df['injury_type']
    )
    
    return df

def main(samples: int = 10000, out_path: Path = Path(__file__).parent / "triage_dataset.csv"):
    """
    Generate enhanced synthetic dataset with:
    - More samples (10,000 default)
    - Balanced classes
    - Realistic severity-based distributions
    - Feature interactions
    """
    print(f"🔬 Generating enhanced dataset with {samples} samples...")
    
    # Balanced distribution: 15% Urgent, 30% Moderate, 55% Minor
    samples_per_class = {
        0: int(samples * 0.15),  # Urgent
        1: int(samples * 0.30),  # Moderate
        2: int(samples * 0.55),  # Minor
    }
    
    print(f"   Class distribution:")
    print(f"      Urgent: {samples_per_class[0]} ({samples_per_class[0]/samples*100:.1f}%)")
    print(f"      Moderate: {samples_per_class[1]} ({samples_per_class[1]/samples*100:.1f}%)")
    print(f"      Minor: {samples_per_class[2]} ({samples_per_class[2]/samples*100:.1f}%)")
    
    # Generate base features
    df = generate_balanced_dataset(samples_per_class)
    
    # Add feature interactions
    print(f"   Adding derived features...")
    df = add_feature_interactions(df)
    
    print(f"   Total features: {df.shape[1] - 1} (including {11} derived features)")
    
    # Persist
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"✅ Enhanced dataset written to {out_path}")
    print(f"   Shape: {df.shape}")
    
    # Save label mapping
    mapping = {
        "0": "Urgent",
        "1": "Moderate",
        "2": "Minor"
    }
    (out_path.parent / "label_mapping.json").write_text(json.dumps(mapping, indent=2))
    
    # Print statistics
    print(f"\n📊 Dataset Statistics:")
    print(f"   Severity distribution:")
    print(df['severity'].value_counts().sort_index())
    
    print(f"\n   Sample vital signs by severity:")
    for severity in [0, 1, 2]:
        severity_name = mapping[str(severity)]
        subset = df[df['severity'] == severity]
        print(f"\n   {severity_name}:")
        print(f"      Avg HR: {subset['heart_rate'].mean():.1f} bpm")
        print(f"      Avg O2: {subset['oxygen_saturation'].mean():.1f}%")
        print(f"      Avg Temp: {subset['temperature'].mean():.1f}°C")
        print(f"      Chest pain: {subset['chest_pain'].mean()*100:.1f}%")

if __name__ == "__main__":
    main()
