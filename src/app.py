"""
app.py

FastAPI application exposing endpoints for:
  - /score_default: compute default risk per account
  - /predict_churn: compute churn risk per client
  - /detect_anomaly: return anomaly scores for transactions

Usage:
    uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from sqlalchemy import create_engine
import pandas as pd
import joblib
import xgboost as xgb
from anomaly import detect_anomalies, load_data as load_tx_data

app = FastAPI(title="Risk & Customer Insights API")

# Resolve paths
ROOT     = Path(__file__).resolve().parent
DB_PATH  = ROOT.parent / "data" / "processed" / "risk_insights.db"
ENGINE   = create_engine(f"sqlite:///{DB_PATH}")
MODEL_DEF= ROOT.parent / "models" / "logreg_default.pkl"
MODEL_CHURN = ROOT.parent / "models" / "xgb_churn.json"

# Load models at startup
logreg_model = joblib.load(MODEL_DEF)
xgb_model    = xgb.Booster()
xgb_model.load_model(str(MODEL_CHURN))

# Request schemas
default_input_fields = ["account_id"]
class DefaultRequest(BaseModel):
    account_id: int

class ChurnRequest(BaseModel):
    client_id: int

class AnomalyRequest(BaseModel):
    contamination: float = 0.05

# Endpoints
@app.post("/score_default")
def score_default(req: DefaultRequest):
    # Load features aggregation
    df_tx = pd.read_sql_table("fact_transactions", ENGINE)
    df_time = pd.read_sql_table("dim_time", ENGINE)
    # Prepare features for the given account_id
    df = df_tx[df_tx["account_id"] == req.account_id].sort_values("transaction_date")
    if df.empty:
        raise HTTPException(status_code=404, detail="Account not found or no transactions")
    total_days = df_time["date"].nunique()
    avg_amount = df["amount"].mean()
    std_amount = df["amount"].std()
    tx_count = df["transaction_id"].count()
    avg_delay = df["transaction_date"].diff().dt.days.dropna().mean()
    X = pd.DataFrame([{
        "avg_amount": avg_amount,
        "std_amount": std_amount,
        "tx_count_per_day": tx_count / total_days,
        "avg_delay_days": avg_delay
    }])
    score = logreg_model.predict_proba(X)[0,1]
    return {"account_id": req.account_id, "default_score": float(score)}

@app.post("/predict_churn")
def predict_churn(req: ChurnRequest):
    # Load and merge
    df_tx = pd.read_sql_table("fact_transactions", ENGINE)
    df_acct = pd.read_sql_table("dim_accounts", ENGINE)
    df = df_tx.merge(df_acct, on="account_id").query(f"client_id=={req.client_id}")
    if df.empty:
        raise HTTPException(status_code=404, detail="Client not found or no transactions")
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["opened_date"] = pd.to_datetime(df["opened_date"])
    tenure = (pd.Timestamp.today() - df["opened_date"].min()).days
    avg_bal = df["amount"].mean()
    total_count = df["transaction_id"].count()
    days_since = (pd.Timestamp.today() - df["transaction_date"].max()).days
    dmat = xgb.DMatrix(pd.DataFrame([{
        "tenure_days": tenure,
        "avg_balance": avg_bal,
        "total_tx_count": total_count,
        "days_since_last": days_since
    }]))
    score = xgb_model.predict(dmat)[0]
    return {"client_id": req.client_id, "churn_score": float(score)}

@app.post("/detect_anomaly")
def detect_anomaly(req: AnomalyRequest):
    df = load_tx_data()
    df_res = detect_anomalies(df.copy(), contamination=req.contamination)
    # return top 100 anomalies
    out = df_res[df_res["is_anomaly"]]
    return out.sort_values("anomaly_score", ascending=False).head(100).to_dict(orient="records")
