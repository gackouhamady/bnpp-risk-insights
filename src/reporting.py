"""
reporting.py

This module automates the extraction and export of key datasets from the processed datamart,
and provides a blueprint for connecting those exports to BI tools such as Power BI or Tableau.


Features:
  1. Reads dimension and fact tables from the SQLite datamart at data/processed/risk_insights.db
  2. Exports each table as a timestamped CSV into data/exports/, preserving historical snapshots
  3. Computes a sample KPI summary (total, average, count by transaction type) and exports it
  4. Demonstrates how these CSVs can be consumed by Power BI / Tableau for interactive dashboards
  5. Supports scheduled daily refresh to keep BI reports up to date
"""

import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parent.parent
DB_URL     = f"sqlite:///{ROOT}/data/processed/risk_insights.db"
EXPORT_DIR = ROOT / "data" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def read_table(table_name: str) -> pd.DataFrame:
    """
    Connects to the datamart and loads the specified table into a pandas DataFrame.

    Parameters:
      table_name (str): Name of the table to load (e.g. "dim_clients", "fact_transactions").

    Returns:
      pd.DataFrame: Contents of the table.
    """
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        df = pd.read_sql_table(table_name, conn)
    return df

def export_to_csv(df: pd.DataFrame, name: str) -> None:
    """
    Exports a DataFrame to a CSV file with a timestamped filename for snapshotting.

    Parameters:
      df (pd.DataFrame): The DataFrame to export.
      name (str): Base name for the output file (e.g. "dim_accounts", "kpi_transactions").

    Side Effects:
      Writes a file named '{name}_{YYYYMMDD_HHMMSS}.csv' in data/exports/.
    """
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    filepath = EXPORT_DIR / f"{name}_{timestamp}.csv"
    df.to_csv(filepath, index=False)
    print(f"[INFO] Exported {name} to {filepath}")

def generate_kpi_summary(df_transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Computes a sample set of KPIs from the transactions fact table.

    KPIs include:
      - Total transaction amount per transaction type
      - Average transaction amount per transaction type
      - Count of transactions per transaction type

    Parameters:
      df_transactions (pd.DataFrame): The transactions DataFrame.

    Returns:
      pd.DataFrame: Aggregated KPI table with columns:
        ['transaction_type', 'total_amount', 'avg_amount', 'count']
    """
    return (
        df_transactions
        .groupby("transaction_type")
        .agg(
            total_amount=("amount", "sum"),
            avg_amount=("amount", "mean"),
            count=("transaction_id", "count")
        )
        .reset_index()
    )

def main() -> None:
    """
    Main orchestration for reporting:
      1. Reads and exports each dimension table
      2. Reads and exports each fact table
      3. Generates and exports a KPI summary for transactions
    """
    # Export dimensions
    for table in ["dim_clients", "dim_accounts", "dim_time"]:
        df = read_table(table)
        export_to_csv(df, table)

    # Export facts
    for table in ["fact_transactions", "fact_events"]:
        df = read_table(table)
        export_to_csv(df, table)

    # Export sample KPI summary
    df_tx = read_table("fact_transactions")
    df_kpi = generate_kpi_summary(df_tx)
    export_to_csv(df_kpi, "kpi_transactions")

if __name__ == "__main__":
    main()
