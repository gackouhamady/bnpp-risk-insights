"""
etl.py

This script implements the full ETL for the “DataHub Risk & Customer Insights” prototype:
  1. Extract raw CSVs from data/raw/
  2. Clean each dataset (accounts, transactions, KYC)
  3. Define a star schema (dimensions: clients, accounts, time; facts: transactions, events)
  4. Populate data/processed/risk_insights.db (SQLite) with all tables

It will automatically create the data/processed/ directory and the SQLite database file if they don’t exist.
"""

import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Date

# ─── Setup project paths ─────────────────────────────────────────────────────────


ROOT           = Path(__file__).resolve().parent.parent
RAW_DIR        = ROOT / "data" / "raw"
PROCESSED_DIR  = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH        = PROCESSED_DIR / "risk_insights.db"
DB_URL         = f"sqlite:///{DB_PATH}"

# ─── Extraction ──────────────────────────────────────────────────────────────────


def extract_raw(raw_dir=RAW_DIR):
    """
    Extract the three raw CSV files and return three DataFrames:
      - accounts, transactions, kyc
    """
    df_accounts     = pd.read_csv(raw_dir / "accounts.csv")
    df_transactions = pd.read_csv(raw_dir / "transactions.csv")
    df_kyc          = pd.read_csv(raw_dir / "kyc.csv")
    return df_accounts, df_transactions, df_kyc

# ─── Cleaning ────────────────────────────────────────────────────────────────────


def clean_accounts(df):
    """
    Clean accounts dimension:
      - Drop duplicate account_id
      - Parse opened_date as datetime
    """
    df = df.drop_duplicates(subset="account_id")
    df["opened_date"] = pd.to_datetime(df["opened_date"])
    return df

def clean_transactions(df):
    """
    Clean transactions:
      - Drop duplicate transaction_id
      - Parse transaction_date as datetime
      - Ensure amount is positive
    """
    df = df.drop_duplicates(subset="transaction_id")
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["amount"] = df["amount"].abs()
    return df

def clean_kyc(df):
    """
    Clean KYC data:
      - Drop duplicate client_id
      - Parse birthdate as datetime
    """
    df = df.drop_duplicates(subset="client_id")
    df["birthdate"] = pd.to_datetime(df["birthdate"])
    return df

# ─── Schema Definition ───────────────────────────────────────────────────────────


def create_engine_and_metadata(db_url=DB_URL):
    """
    Create the SQLAlchemy engine and MetaData container.
    """
    engine = create_engine(db_url, echo=False)
    metadata = MetaData()
    return engine, metadata

def define_star_schema(metadata):
    """
    Declare star schema tables: dimensions and facts.
    """
    # Dimensions
    dim_clients = Table("dim_clients", metadata,
        Column("client_id", Integer, primary_key=True),
        Column("name", String),
        Column("birthdate", Date),
        Column("country", String),
    )
    dim_accounts = Table("dim_accounts", metadata,
        Column("account_id", Integer, primary_key=True),
        Column("client_id", Integer),
        Column("account_type", String),
        Column("opened_date", Date),
    )
    dim_time = Table("dim_time", metadata,
        Column("time_id", Integer, primary_key=True, autoincrement=True),
        Column("date", Date, unique=True),
        Column("year", Integer),
        Column("month", Integer),
        Column("day", Integer),
        Column("quarter", Integer),
        Column("weekday", Integer),
    )

    # Fact tables
    fact_transactions = Table("fact_transactions", metadata,
        Column("transaction_id", Integer, primary_key=True),
        Column("account_id", Integer),
        Column("client_id", Integer),
        Column("time_id", Integer),
        Column("amount", Float),
        Column("transaction_type", String),
    )
    fact_events = Table("fact_events", metadata,
        Column("event_id", Integer, primary_key=True, autoincrement=True),
        Column("client_id", Integer),
        Column("account_id", Integer),
        Column("time_id", Integer),
        Column("event_type", String),
    )

    return {
        "dim_clients": dim_clients,
        "dim_accounts": dim_accounts,
        "dim_time": dim_time,
        "fact_transactions": fact_transactions,
        "fact_events": fact_events,
    }

# ─── Time Dimension Population ──────────────────────────────────────────────────


def populate_time_dimension(df_transactions, engine):
    """
    Build and load the time dimension from unique transaction dates.
    """
    df_time = pd.DataFrame({
        "date": pd.to_datetime(df_transactions["transaction_date"]).dt.date.unique()
    })
    df_time["year"]    = pd.to_datetime(df_time["date"]).dt.year
    df_time["month"]   = pd.to_datetime(df_time["date"]).dt.month
    df_time["day"]     = pd.to_datetime(df_time["date"]).dt.day
    df_time["quarter"] = pd.to_datetime(df_time["date"]).dt.quarter
    df_time["weekday"] = pd.to_datetime(df_time["date"]).dt.weekday
    df_time.to_sql("dim_time", engine, if_exists="replace", index=False)
    return df_time

# ─── Load Data ─────────────────────────────────────────────────────────────────


def load_data(df_accounts, df_transactions, df_kyc, engine, schema_tables):
    """
    Load cleaned DataFrames into the database following the star schema:
      - Dimensions: dim_clients, dim_accounts, dim_time
      - Facts: fact_transactions, fact_events
    """
    # 1) Dimensions
    df_kyc.to_sql("dim_clients", engine, if_exists="replace", index=False)
    df_accounts.to_sql("dim_accounts", engine, if_exists="replace", index=False)
    df_time = populate_time_dimension(df_transactions, engine)

    # 2) Fact: transactions
    df_tx = df_transactions.copy()
    # map dates → time_id (index +1 matches SQLite autoincrement)
    df_tx["time_id"] = df_tx["transaction_date"].dt.date.map(
        {row["date"]: idx+1 for idx, row in df_time.iterrows()}
    )
    # map accounts → client_id
    df_tx["client_id"] = df_tx["account_id"].map(
        dict(zip(df_accounts["account_id"], df_accounts["client_id"]))
    )
    df_tx.to_sql("fact_transactions", engine, if_exists="replace", index=False)

    # 3) Fact: events (empty placeholder)
    df_events = pd.DataFrame(columns=["client_id", "account_id", "time_id", "event_type"])
    df_events.to_sql("fact_events", engine, if_exists="replace", index=False)


# ─── Main ───────────────────────────────────────────────────────────────────────
def main():
    # 1) Extract
    accts, txs, kyc = extract_raw()

    # 2) Clean
    accts = clean_accounts(accts)
    txs   = clean_transactions(txs)
    kyc   = clean_kyc(kyc)

    # 3) Schema and tables
    engine, metadata = create_engine_and_metadata()
    tables = define_star_schema(metadata)
    metadata.create_all(engine)  # create tables in SQLite file

    # 4) Load into star schema
    load_data(accts, txs, kyc, engine, tables)

    print(f"ETL complete: datamart ready at {DB_PATH}")

if __name__ == "__main__":
    main()
