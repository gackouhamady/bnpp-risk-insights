"""
model_default.py

Train and evaluate a logistic regression model for default scoring,
handling missing feature values via imputation.

Steps:
  1. Resolve the path to the processed datamart
  2. Load transaction and time dimension tables
  3. Aggregate features per account:
     - avg_amount: mean transaction amount
     - std_amount: standard deviation of amounts
     - tx_count_per_day: transactions per day
     - avg_delay_days: average days between transactions
  4. Simulate or load the 'is_default' target column if missing
  5. Handle missing feature values via imputation
  6. Split data into train and test sets
  7. Build an ML pipeline (imputation + scaling + logistic regression)
  8. Train the model
  9. Evaluate performance (AUC, confusion matrix, classification report)
 10. Save the trained model to disk
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, confusion_matrix, classification_report

# ─── 1) Resolve database path and create engine ─────────────────────────────────
ROOT    = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "processed" / "risk_insights.db"
engine  = create_engine(f"sqlite:///{DB_PATH}")

# ─── 2) Load raw transactions and time dimension ─────────────────────────────────
df_tx   = pd.read_sql_table("fact_transactions", engine)
df_time = pd.read_sql_table("dim_time",         engine)

# Compute total number of unique days for frequency calculation
total_days = df_time["date"].nunique()

# ─── 3) Aggregate features by account_id ────────────────────────────────────────
# Sort to compute inter-transaction delays correctly
df_tx = df_tx.sort_values(["account_id", "transaction_date"])

features = (
    df_tx
    .groupby("account_id")
    .agg(
        avg_amount     = ("amount",         "mean"),                       # mean transaction amount
        std_amount     = ("amount",         "std"),                        # standard deviation of amounts
        tx_count       = ("transaction_id", "count"),                      # total number of transactions
        avg_delay_days = ("transaction_date", lambda d:                    # average days between transactions
                                       d.diff().dt.days.dropna().mean())
    )
    .reset_index()
)

# Calculate transactions per day
features["tx_count_per_day"] = features["tx_count"] / total_days

# ─── 4) Simulate or load the 'is_default' target ───────────────────────────────
if "is_default" not in features.columns:
    # Example simulation: mark top 20% accounts by avg_amount as defaults
    threshold = features["avg_amount"].quantile(0.8)
    features["is_default"] = (features["avg_amount"] > threshold).astype(int)

# ─── 5) Handle missing values via imputation ───────────────────────────────────
# We'll impute missing feature values with column mean
imputer = SimpleImputer(missing_values=np.nan, strategy="mean")

# Prepare feature matrix and target vector
X = features[["avg_amount", "std_amount", "tx_count_per_day", "avg_delay_days"]]
y = features["is_default"]  # 0 = no default, 1 = default

# Apply imputation before splitting
X_imputed = pd.DataFrame(
    imputer.fit_transform(X),
    columns=X.columns,
    index=X.index
)

# ─── 6) Split data into train and test sets ────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_imputed, y,
    test_size=0.3,
    stratify=y,
    random_state=42
)

# ─── 7) Build ML pipeline ──────────────────────────────────────────────────────
pipe = Pipeline([
    ("scaler", StandardScaler()),                         # standardize features
    ("clf",    LogisticRegression(solver="liblinear",     # logistic regression classifier
                                  random_state=42))
])

# ─── 8) Train the model ────────────────────────────────────────────────────────
pipe.fit(X_train, y_train)

# ─── 9) Evaluate performance ──────────────────────────────────────────────────
# Predict probabilities for positive class
y_proba = pipe.predict_proba(X_test)[:, 1]
# Predict class labels
y_pred  = pipe.predict(X_test)

# Compute metrics
auc_score = roc_auc_score(y_test, y_proba)
cm        = confusion_matrix(y_test, y_pred)
report    = classification_report(y_test, y_pred)

print("=== Default Scoring Model Evaluation ===")
print(f"AUC: {auc_score:.4f}")
print("Confusion Matrix:")
print(cm)
print("Classification Report:")
print(report)

# ─── 10) Save the trained model ─────────────────────────────────────────────────
model_dir = ROOT / "models"
model_dir.mkdir(exist_ok=True)
model_path = model_dir / "logreg_default.pkl"
joblib.dump(pipe, model_path)
print(f"Model saved to {model_path}")
