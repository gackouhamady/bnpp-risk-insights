"""
pipeline.py

Orchestrate the end-to-end workflow:
  1. Run ETL to build the datamart
  2. Apply default scoring (logistic regression) with imputation
  3. Apply churn prediction (XGBoost)
  4. Detect anomalies (Isolation Forest)
  5. Log parameters and metrics in MLflow
  6. Generate a single JSON report per run

Usage:
    python src/pipeline.py
"""
import json
from datetime import datetime
from pathlib import Path

import mlflow
import pandas as pd
import joblib
import xgboost as xgb
from sqlalchemy import create_engine
from sklearn.impute import SimpleImputer

# Import ETL and anomaly modules
from etl import main as run_etl
from anomaly import load_data as load_tx_data, detect_anomalies

# ─── Configuration ─────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parent.parent
DB_PATH     = ROOT / "data" / "processed" / "risk_insights.db"
REPORT_DIR  = ROOT / "data" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_DEF   = ROOT / "models" / "logreg_default.pkl"
MODEL_CHURN = ROOT / "models" / "xgb_churn.json"

# ─── 1) ETL ─────────────────────────────────────────────────────────────────────
run_etl()
engine = create_engine(f"sqlite:///{DB_PATH}")

# ─── 2) Default Scoring ─────────────────────────────────────────────────────────
df_tx     = pd.read_sql_table("fact_transactions", engine)
df_time   = pd.read_sql_table("dim_time",        engine)

total_days = df_time['date'].nunique()
df_tx = df_tx.sort_values(["account_id", "transaction_date"])

features_def = (
    df_tx.groupby("account_id").agg(
        avg_amount     = ("amount",         "mean"),
        std_amount     = ("amount",         "std"),
        tx_count       = ("transaction_id", "count"),
        avg_delay_days = ("transaction_date", lambda d: d.diff().dt.days.dropna().mean())
    )
    .reset_index()
)
features_def['tx_count_per_day'] = features_def['tx_count'] / total_days

# Impute missing values
X_def = features_def[["avg_amount","std_amount","tx_count_per_day","avg_delay_days"]]
imputer_def = SimpleImputer(strategy="mean")
X_def_imputed = imputer_def.fit_transform(X_def)

# Load and predict
def_model = joblib.load(MODEL_DEF)
def_prob = def_model.predict_proba(X_def_imputed)[:, 1]
features_def['default_risk'] = def_prob

# ─── 3) Churn Prediction ───────────────────────────────────────────────────────
df_tx   = pd.read_sql_table("fact_transactions", engine)
df_acct = pd.read_sql_table("dim_accounts",      engine)

df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])
df_acct['opened_date']    = pd.to_datetime(df_acct['opened_date'])

df_merge = df_tx.merge(df_acct, on='account_id', suffixes=('_tx','_acct'))
df_merge['client_id'] = df_merge['client_id_tx']

features_churn = (
    df_merge.groupby('client_id').agg(
        tenure_days    = ('opened_date',      lambda d: (pd.Timestamp.today() - d.min()).days),
        avg_balance    = ('amount',            'mean'),
        total_tx_count = ('transaction_id',    'count'),
        days_since_last= ('transaction_date',  lambda d: (pd.Timestamp.today() - d.max()).days)
    )
    .reset_index()
)

# Load XGBoost model and predict
churn_model = xgb.Booster()
churn_model.load_model(str(MODEL_CHURN))
dmat = xgb.DMatrix(
    features_churn[['tenure_days','avg_balance','total_tx_count','days_since_last']]
)
churn_prob = churn_model.predict(dmat)
features_churn['churn_risk'] = churn_prob

# ─── 4) Anomaly Detection ──────────────────────────────────────────────────────
df_anom = load_tx_data().pipe(lambda df: detect_anomalies(df, contamination=0.05))

# Convert datetime to string for JSON
if 'transaction_date' in df_anom.columns:
    df_anom['transaction_date'] = df_anom['transaction_date'].astype(str)

# ─── 5) MLflow Tracking ────────────────────────────────────────────────────────
mlflow.set_experiment("Risk_and_Customer_Insights")
with mlflow.start_run():
    mlflow.log_artifact(str(MODEL_DEF), artifact_path='models')
    mlflow.log_artifact(str(MODEL_CHURN), artifact_path='models')
    mlflow.log_metric('avg_default_risk', float(features_def['default_risk'].mean()))
    mlflow.log_metric('avg_churn_risk',   float(features_churn['churn_risk'].mean()))
    mlflow.log_metric('n_anomalies',      int(df_anom['is_anomaly'].sum()))

# ─── 6) Generate JSON Report ───────────────────────────────────────────────────
report = {
    'timestamp': datetime.utcnow().isoformat(),
    'default_risk_summary': features_def[['account_id','default_risk']].to_dict(orient='records'),
    'churn_risk_summary':   features_churn[['client_id','churn_risk']].to_dict(orient='records'),
    'anomalies':            df_anom[df_anom['is_anomaly']].to_dict(orient='records')
}

report_path = REPORT_DIR / f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)

print(f"Pipeline complete. Report written to {report_path}")
