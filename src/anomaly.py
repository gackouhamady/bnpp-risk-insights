"""
anomaly.py

Detect transaction-level anomalies using Isolation Forest,
and provide a Streamlit interface to explore outliers.

Steps:
  1. Resolve the path to the processed datamart
  2. Load the fact_transactions table and compute tx_per_account
  3. Fit an IsolationForest and compute an anomaly score for each transaction
  4. Expose a Streamlit app to:
       - adjust the contamination level
       - view score distribution correctly
       - inspect the top-N most anomalous transactions
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest

# ─── 1) Resolve DB path and connect ───────────────────────────────────────────────
ROOT    = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "processed" / "risk_insights.db"
engine  = create_engine(f"sqlite:///{DB_PATH}")

@st.cache_data
def load_data():
    """Load transactions and compute frequency feature."""
    df_tx = pd.read_sql_table("fact_transactions", engine)
    # compute transactions per account
    freq = (
        df_tx
        .groupby("account_id")["transaction_id"]
        .count()
        .rename("tx_per_account")
    )
    df = df_tx.merge(freq, on="account_id")
    return df

def detect_anomalies(df: pd.DataFrame, contamination: float):
    """
    Fit IsolationForest on ['amount', 'tx_per_account'] and
    return the DataFrame with anomaly_score and is_anomaly flag.
    """
    X = df[["amount", "tx_per_account"]].to_numpy()
    iso = IsolationForest(contamination=contamination, random_state=42)
    iso.fit(X)
    # decision_function gives larger = more normal, so invert it
    scores = -iso.decision_function(X)
    df["anomaly_score"] = scores
    threshold = np.quantile(scores, 1 - contamination)
    df["is_anomaly"] = df["anomaly_score"] >= threshold
    return df

def main():
    st.title("🚨 Transaction Anomaly Detection")
    st.markdown("""
        Use Isolation Forest on transaction amount and per-account frequency.
        Adjust the contamination level to control the fraction of flagged outliers.
    """)

    df = load_data()

    contamination = st.slider(
        "Contamination (fraction of anomalies)", 
        min_value=0.01, max_value=0.20, value=0.05, step=0.01
    )

    df_result = detect_anomalies(df.copy(), contamination)

    st.subheader("Anomaly Score Distribution")
    # compute histogram bins and counts
    counts, bin_edges = np.histogram(df_result["anomaly_score"], bins=50)
    hist_df = pd.DataFrame(
        {"count": counts}, 
        index=pd.IntervalIndex.from_breaks(bin_edges)
    )
    st.bar_chart(hist_df)

    st.subheader(f"Top {min(20, int(len(df_result)*contamination))} Anomalous Transactions")
    st.dataframe(
        df_result
        .loc[df_result["is_anomaly"]]
        .sort_values("anomaly_score", ascending=False)
        .head(20)
        .reset_index(drop=True)
    )

if __name__ == "__main__":
    main()
