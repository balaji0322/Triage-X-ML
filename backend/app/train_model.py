# backend/app/train_model.py
import joblib
import json
import logging
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

# ----------------------------------------------------------------------
# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
DATA_PATH = Path(__file__).parent.parent / "data" / "triage_dataset.csv"
MODEL_PATH = Path(__file__).parent.parent / "models" / "triage_model.pkl"
LABEL_MAP_PATH = Path(__file__).parent.parent / "data" / "label_mapping.json"

# Global to store class remapping
REVERSE_CLASS_MAP = None

# ----------------------------------------------------------------------
def load_data():
    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns="severity")
    y = df["severity"].astype(int)
    
    # Check if we need to remap classes to be 0-indexed
    unique_classes = sorted(y.unique())
    logger.info(f"Original classes in dataset: {unique_classes}")
    
    # If classes don't start at 0, remap them
    if min(unique_classes) != 0:
        logger.info("Remapping classes to be 0-indexed for XGBoost")
        class_mapping = {old: new for new, old in enumerate(unique_classes)}
        y = y.map(class_mapping)
        logger.info(f"Class mapping: {class_mapping}")
        
        # Update label mapping file to reflect this
        reverse_mapping = {new: old for old, new in class_mapping.items()}
        global REVERSE_CLASS_MAP
        REVERSE_CLASS_MAP = reverse_mapping
    
    return X, y

def build_preprocess(X):
    # numeric columns ----------------------------------------------------
    numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    # In our synthetic set, gender is the only categorical
    categorical_cols = ["gender"]
    
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    
    preproc = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ]
    )
    return preproc

def train():
    logger.info("Loading data …")
    X, y = load_data()
    
    logger.info("Splitting train / test …")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
    
    logger.info("Building preprocessing pipeline …")
    preproc = build_preprocess(X_train)
    
    # --------------------------------------------------------
    # XGBoost – we use built‑in handling of class imbalance
    # scale_pos_weight is only for binary, so we give class_weights via sample_weight
    class_counts = pd.Series(y_train).value_counts().sort_index()
    # Inverse frequency weighting
    class_weights = {i: (len(y_train) / (len(class_counts) * cnt)) for i, cnt in class_counts.items()}
    sample_weight = y_train.map(class_weights)
    
    # Determine number of classes from training data
    num_classes = len(y_train.unique())
    logger.info(f"Training with {num_classes} classes")
    
    xgb_model = XGBClassifier(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.8,
        objective="multi:softprob",
        eval_metric="mlogloss",
        num_class=num_classes,
        use_label_encoder=False,
        random_state=42,
        n_jobs=-1,
    )
    
    pipe = Pipeline(
        steps=[
            ("preprocess", preproc),
            ("model", xgb_model),
        ]
    )
    
    logger.info("Training model …")
    pipe.fit(X_train, y_train, model__sample_weight=sample_weight)
    
    # ------------------------------------------------------------------
    # Evaluation
    from sklearn.metrics import accuracy_score, classification_report, log_loss
    
    y_pred = pipe.predict(X_test)
    y_proba = pipe.predict_proba(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    loss = log_loss(y_test, y_proba)
    logger.info(f"Test accuracy: {acc:.4f}")
    logger.info(f"Test log‑loss: {loss:.4f}")
    
    # Get target names based on actual classes present
    all_labels = ["Immediate", "Urgent", "Moderate", "Minor"]
    if REVERSE_CLASS_MAP:
        target_names = [all_labels[REVERSE_CLASS_MAP[i]] for i in sorted(y_test.unique())]
    else:
        target_names = [all_labels[i] for i in sorted(y_test.unique())]
    
    logger.info("\n" + classification_report(y_test, y_pred, target_names=target_names))
    
    # ------------------------------------------------------------------
    # Save model
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    logger.info(f"Saved trained pipeline to {MODEL_PATH}")
    
    # Save label mapping (used by the API)
    # If we remapped classes, save the correct mapping
    if REVERSE_CLASS_MAP:
        label_map = {str(new_idx): all_labels[old_idx] for new_idx, old_idx in REVERSE_CLASS_MAP.items()}
    else:
        label_map = json.load(open(LABEL_MAP_PATH))
    
    joblib.dump(label_map, MODEL_PATH.parent / "label_map.pkl")
    logger.info(f"Saved label‑mapping pickle for API: {label_map}")
    
    # ------------------------------------------------------------------
    # Feature importance (global) – XGBoost provides it
    booster = pipe.named_steps["model"].get_booster()
    importance = booster.get_score(importance_type="gain")
    # sort & keep top N
    importance = dict(sorted(importance.items(), key=lambda item: item[1], reverse=True)[:20])
    joblib.dump(importance, MODEL_PATH.parent / "feature_importance.pkl")
    logger.info("Saved feature importance")

if __name__ == "__main__":
    train()
