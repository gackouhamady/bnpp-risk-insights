"""
model_churn.py

Train and evaluate an XGBoost model for customer churn prediction,
handling missing values and dynamic database resolution.

Steps:
  1. Resolve the path to the processed datamart
  2. Load and merge account and transaction data
  3. Aggregate features per client:
     - tenure_days: days since account opening
     - avg_balance: mean transaction amount (proxy for balance)
     - total_tx_count: total number of transactions
     - days_since_last: days since last transaction
  4. Simulate or load the 'is_churn' target column if missing
  5. Handle missing feature values via imputation
  6. Split data into train and test sets
  7. Convert to XGBoost DMatrix format
  8. Train the XGBoost model with AUC evaluation
  9. Evaluate performance (AUC, classification report)
 10. Save the trained model to disk
"""

import joblib
import pandas as pd
import numpy as np
import xgboost as xgb
from pathlib import Path
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score, classification_report

# ─── 1) Resolve database path and create engine ─────────────────────────────────
ROOT    = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "processed" / "risk_insights.db"
engine  = create_engine(f"sqlite:///{DB_PATH}")

# ─── 2) Load account + transaction data ─────────────────────────────────────────
df_tx   = pd.read_sql_table("fact_transactions", engine)
df_acct = pd.read_sql_table("dim_accounts",      engine)

# Ensure datetime types
df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"])
df_acct["opened_date"]    = pd.to_datetime(df_acct["opened_date"])

# Merge on account_id, suffix overlapping columns
# fact_transactions and dim_accounts both have client_id; we keep client_id from transactions
df = df_tx.merge(
    df_acct,
    on="account_id",
    suffixes=("_tx", "_acct")
)
# Standardize client_id column
df["client_id"] = df["client_id_tx"]
# Drop redundant columns
df = df.drop(columns=["client_id_tx", "client_id_acct"])

# ─── 3) Aggregate features by client_id ────────────────────────────────────────
# Sort to compute recency correctly
df = df.sort_values(["client_id", "transaction_date"])
features = (
    df
    .groupby("client_id")
    .agg(
        tenure_days     = ("opened_date",      lambda d: (pd.Timestamp.today() - d.min()).days),
        avg_balance     = ("amount",           "mean"),
        total_tx_count  = ("transaction_id",   "count"),
        days_since_last = ("transaction_date", lambda d: (pd.Timestamp.today() - d.max()).days)
    )
    .reset_index()
)

# ─── 4) Simulate or load the 'is_churn' target ───────────────────────────────
if "is_churn" not in features.columns:
    threshold = features["days_since_last"].quantile(0.8)
    features["is_churn"] = (features["days_since_last"] > threshold).astype(int)

# ─── 5) Handle missing values via imputation ───────────────────────────────────
imputer = SimpleImputer(missing_values=np.nan, strategy="mean")
X = features[["tenure_days", "avg_balance", "total_tx_count", "days_since_last"]]
y = features["is_churn"]
X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

# ─── 6) Split data into train and test sets ────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_imputed, y,
    test_size=0.3,
    stratify=y,
    random_state=42
)

# ─── 7) Convert datasets to XGBoost DMatrix ───────────────────────────────────
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest  = xgb.DMatrix(X_test,  label=y_test)

# ─── 8) Train XGBoost model with AUC as evaluation metric ─────────────────────
params    = {"objective":"binary:logistic","eval_metric":"auc","seed":42}
num_round = 100
bst       = xgb.train(params, dtrain, num_boost_round=num_round,
                      evals=[(dtrain, "train"), (dtest, "test")], verbose_eval=False)

# ─── 9) Evaluate performance ───────────────────────────────────────────────────
y_proba   = bst.predict(dtest)
y_pred    = (y_proba > 0.5).astype(int)
auc_score = roc_auc_score(y_test, y_proba)
report    = classification_report(y_test, y_pred)
print("=== Churn Prediction Model Evaluation ===")
print(f"AUC: {auc_score:.4f}")
print("Classification Report:")
print(report)

# ─── 10) Save the trained model ─────────────────────────────────────────────────
model_dir  = ROOT / "models"
model_dir.mkdir(exist_ok=True)
model_path = model_dir / "xgb_churn.json"
bst.save_model(model_path)
print(f"Model saved to {model_path}")
