# backend/app/train_model.py
import joblib
import json
import logging
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
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
    """Load and validate dataset."""
    df = pd.read_csv(DATA_PATH)
    logger.info(f"Loaded dataset: {df.shape}")
    
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
    
    logger.info(f"Class distribution:\n{y.value_counts().sort_index()}")
    
    return X, y

def build_preprocess(X):
    """Build advanced preprocessing pipeline."""
    # Identify feature types
    numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = ["gender"] if "gender" in X.columns else []
    
    logger.info(f"Numeric features: {len(numeric_cols)}")
    logger.info(f"Categorical features: {len(categorical_cols)}")
    
    # Use RobustScaler for better handling of outliers
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", RobustScaler()),  # More robust to outliers than StandardScaler
        ]
    )
    
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
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
    """Train advanced XGBoost model with optimized hyperparameters."""
    logger.info("=" * 70)
    logger.info("🚀 ADVANCED MODEL TRAINING")
    logger.info("=" * 70)
    
    logger.info("\n📂 Loading data...")
    X, y = load_data()
    
    logger.info("\n✂️  Splitting train/validation/test sets...")
    # First split: 80% train+val, 20% test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Second split: 75% train, 25% validation (of the 80%)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
    )
    
    logger.info(f"   Train set: {X_train.shape[0]} samples")
    logger.info(f"   Validation set: {X_val.shape[0]} samples")
    logger.info(f"   Test set: {X_test.shape[0]} samples")
    
    logger.info("\n🔧 Building preprocessing pipeline...")
    preproc = build_preprocess(X_train)
    
    # --------------------------------------------------------
    # Advanced XGBoost with optimized hyperparameters
    # --------------------------------------------------------
    
    # Calculate class weights for imbalanced data
    class_counts = pd.Series(y_train).value_counts().sort_index()
    class_weights = {i: (len(y_train) / (len(class_counts) * cnt)) for i, cnt in class_counts.items()}
    sample_weight = y_train.map(class_weights)
    
    logger.info(f"\n⚖️  Class weights: {class_weights}")
    
    # Determine number of classes
    num_classes = len(y_train.unique())
    logger.info(f"   Training with {num_classes} classes")
    
    # Advanced XGBoost configuration
    xgb_model = XGBClassifier(
        # Tree parameters
        n_estimators=500,           # More trees for better learning
        max_depth=8,                # Deeper trees for complex patterns
        min_child_weight=3,         # Minimum sum of instance weight in a child
        
        # Learning parameters
        learning_rate=0.03,         # Lower learning rate with more estimators
        
        # Regularization
        gamma=0.1,                  # Minimum loss reduction for split
        subsample=0.85,             # Subsample ratio of training instances
        colsample_bytree=0.85,      # Subsample ratio of columns per tree
        colsample_bylevel=0.85,     # Subsample ratio of columns per level
        reg_alpha=0.1,              # L1 regularization
        reg_lambda=1.0,             # L2 regularization
        
        # Other parameters
        objective="multi:softprob",
        eval_metric="mlogloss",
        num_class=num_classes,
        use_label_encoder=False,
        random_state=42,
        n_jobs=-1,
        tree_method='hist',         # Faster histogram-based algorithm
        
        # Early stopping
        early_stopping_rounds=50,
    )
    
    # Build full pipeline
    pipe = Pipeline(
        steps=[
            ("preprocess", preproc),
            ("model", xgb_model),
        ]
    )
    
    logger.info("\n🎯 Training model with early stopping...")
    
    # Fit with validation set for early stopping
    pipe.fit(
        X_train, y_train,
        model__sample_weight=sample_weight,
        model__eval_set=[(pipe.named_steps['preprocess'].fit_transform(X_val), y_val)],
        model__verbose=False
    )
    
    # Get best iteration
    best_iteration = pipe.named_steps['model'].best_iteration
    logger.info(f"   Best iteration: {best_iteration}")
    
    # ------------------------------------------------------------------
    # Cross-validation (without early stopping for CV)
    # ------------------------------------------------------------------
    logger.info("\n🔄 Performing 5-fold cross-validation...")
    
    # Create a model without early stopping for CV
    xgb_cv = XGBClassifier(
        n_estimators=500,
        max_depth=8,
        min_child_weight=3,
        learning_rate=0.03,
        gamma=0.1,
        subsample=0.85,
        colsample_bytree=0.85,
        colsample_bylevel=0.85,
        reg_alpha=0.1,
        reg_lambda=1.0,
        objective="multi:softprob",
        eval_metric="mlogloss",
        num_class=num_classes,
        use_label_encoder=False,
        random_state=42,
        n_jobs=-1,
        tree_method='hist',
    )
    
    pipe_cv = Pipeline([
        ("preprocess", preproc),
        ("model", xgb_cv),
    ])
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(
        pipe_cv, X_temp, y_temp, cv=cv, scoring='accuracy', n_jobs=-1
    )
    logger.info(f"   CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    logger.info(f"   CV Scores: {[f'{s:.4f}' for s in cv_scores]}")
    
    # ------------------------------------------------------------------
    # Evaluation on all sets
    # ------------------------------------------------------------------
    from sklearn.metrics import (
        accuracy_score, classification_report, log_loss,
        precision_recall_fscore_support, confusion_matrix
    )
    
    logger.info("\n📊 Model Performance:")
    
    # Training set
    y_train_pred = pipe.predict(X_train)
    train_acc = accuracy_score(y_train, y_train_pred)
    logger.info(f"   Training accuracy: {train_acc:.4f}")
    
    # Validation set
    y_val_pred = pipe.predict(X_val)
    val_acc = accuracy_score(y_val, y_val_pred)
    logger.info(f"   Validation accuracy: {val_acc:.4f}")
    
    # Test set
    y_test_pred = pipe.predict(X_test)
    y_test_proba = pipe.predict_proba(X_test)
    test_acc = accuracy_score(y_test, y_test_pred)
    test_loss = log_loss(y_test, y_test_proba)
    
    logger.info(f"   Test accuracy: {test_acc:.4f}")
    logger.info(f"   Test log-loss: {test_loss:.4f}")
    
    # Check for overfitting
    if train_acc - test_acc > 0.05:
        logger.warning(f"   ⚠️  Possible overfitting detected (train-test gap: {train_acc - test_acc:.4f})")
    else:
        logger.info(f"   ✅ Good generalization (train-test gap: {train_acc - test_acc:.4f})")
    
    # Detailed classification report
    all_labels = ["Immediate", "Urgent", "Moderate", "Minor"]
    if REVERSE_CLASS_MAP:
        target_names = [all_labels[REVERSE_CLASS_MAP[i]] for i in sorted(y_test.unique())]
    else:
        target_names = [all_labels[i] for i in sorted(y_test.unique())]
    
    logger.info("\n📈 Detailed Classification Report (Test Set):")
    logger.info("\n" + classification_report(y_test, y_test_pred, target_names=target_names))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_test_pred)
    logger.info("🔀 Confusion Matrix (Test Set):")
    logger.info(f"\n{cm}\n")
    
    # Per-class metrics
    precision, recall, f1, support = precision_recall_fscore_support(y_test, y_test_pred)
    logger.info("📊 Per-Class Metrics:")
    for i, (p, r, f, s) in enumerate(zip(precision, recall, f1, support)):
        logger.info(f"   {target_names[i]:<12} P:{p:.4f} R:{r:.4f} F1:{f:.4f} Support:{s}")
    
    # ------------------------------------------------------------------
    # Save model
    # ------------------------------------------------------------------
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    logger.info(f"\n💾 Model saved to {MODEL_PATH}")
    
    # Save label mapping
    if REVERSE_CLASS_MAP:
        label_map = {str(new_idx): all_labels[old_idx] for new_idx, old_idx in REVERSE_CLASS_MAP.items()}
    else:
        label_map = json.load(open(LABEL_MAP_PATH))
    
    joblib.dump(label_map, MODEL_PATH.parent / "label_map.pkl")
    logger.info(f"💾 Label mapping saved: {label_map}")
    
    # ------------------------------------------------------------------
    # Feature importance
    # ------------------------------------------------------------------
    logger.info("\n🎯 Extracting feature importance...")
    booster = pipe.named_steps["model"].get_booster()
    importance = booster.get_score(importance_type="gain")
    
    # Sort and save top features
    importance = dict(sorted(importance.items(), key=lambda item: item[1], reverse=True))
    joblib.dump(importance, MODEL_PATH.parent / "feature_importance.pkl")
    
    logger.info("   Top 10 features by importance:")
    for i, (feat, score) in enumerate(list(importance.items())[:10], 1):
        logger.info(f"      {i:2d}. {feat:<15} {score:8.2f}")
    
    # ------------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------------
    logger.info("\n" + "=" * 70)
    logger.info("✅ TRAINING COMPLETE")
    logger.info("=" * 70)
    logger.info(f"   Final Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")
    logger.info(f"   Cross-Validation: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    logger.info(f"   Model saved: {MODEL_PATH}")
    logger.info("=" * 70)

if __name__ == "__main__":
    train()
