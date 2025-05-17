import pandas as pd
import pytest
from pathlib import Path
from sqlalchemy import create_engine, inspect

import etl

# ─── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture
def raw_data_dir(tmp_path):
    """
    Create a temporary raw data directory with sample CSV files.
    """
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)

    # Sample accounts.csv
    df_accts = pd.DataFrame({
        "account_id": [1, 1, 2],
        "client_id": [10, 20, 20],
        "account_type": ["A", "A", "B"],
        "opened_date": ["2020-01-01", "2020-01-01", "2021-06-15"],
    })
    df_accts.to_csv(raw_dir / "accounts.csv", index=False)

    # Sample transactions.csv
    df_tx = pd.DataFrame({
        "transaction_id": [100, 100, 101],
        "account_id": [1, 2, 2],
        "transaction_date": ["2022-03-01", "2022-03-01", "2022-03-02"],
        "amount": [-50, -50, 75],
        "transaction_type": ["debit", "debit", "credit"],
    })
    df_tx.to_csv(raw_dir / "transactions.csv", index=False)

    # Sample kyc.csv
    df_kyc = pd.DataFrame({
        "client_id": [10, 10, 20],
        "name": ["Alice", "Alice", "Bob"],
        "birthdate": ["1990-05-10", "1990-05-10", "1985-07-20"],
        "country": ["FR", "FR", "US"],
    })
    df_kyc.to_csv(raw_dir / "kyc.csv", index=False)

    return raw_dir.parent  # returns tmp_path/data

# ─── Unit Tests ────────────────────────────────────────────────────────────────

def test_extract_raw(tmp_path, raw_data_dir, monkeypatch):
    # Point etl.RAW_DIR to our fixture
    monkeypatch.setattr(etl, "RAW_DIR", raw_data_dir / "raw")
    df_accts, df_tx, df_kyc = etl.extract_raw()

    # Basic assertions
    assert isinstance(df_accts, pd.DataFrame)
    assert len(df_accts) == 3
    assert "account_id" in df_accts.columns

    assert isinstance(df_tx, pd.DataFrame)
    assert df_tx["amount"].dtype == float

    assert isinstance(df_kyc, pd.DataFrame)
    assert "birthdate" in df_kyc.columns


def test_clean_accounts():
    df = pd.DataFrame({
        "account_id": [1, 1, 2],
        "opened_date": ["2020-01-01", "2020-01-01", "2021-06-15"],
    })
    cleaned = etl.clean_accounts(df)
    assert cleaned["account_id"].nunique() == 2
    assert cleaned["opened_date"].dtype == "datetime64[ns]"


def test_clean_transactions():
    df = pd.DataFrame({
        "transaction_id": [100, 100, 101],
        "transaction_date": ["2022-03-01", "2022-03-01", "2022-03-02"],
        "amount": [-50, -50, 75],
    })
    cleaned = etl.clean_transactions(df)
    assert cleaned["transaction_id"].nunique() == 2
    assert cleaned["amount"].min() >= 0
    assert cleaned["transaction_date"].dtype == "datetime64[ns]"


def test_clean_kyc():
    df = pd.DataFrame({
        "client_id": [10, 10, 20],
        "birthdate": ["1990-05-10", "1990-05-10", "1985-07-20"],
    })
    cleaned = etl.clean_kyc(df)
    assert cleaned["client_id"].nunique() == 2
    assert cleaned["birthdate"].dtype == "datetime64[ns]"


def test_full_etl(tmp_path, raw_data_dir, monkeypatch):
    # Redirect ROOT and RAW_DIR
    project_root = tmp_path
    monkeypatch.setattr(etl, "ROOT", project_root)
    monkeypatch.setattr(etl, "RAW_DIR", raw_data_dir / "raw")

    # Run ETL
    etl.main()

    # Check database file
    db_file = project_root / "data" / "processed" / "risk_insights.db"
    assert db_file.exists(), f"Database file not found at {db_file}"

    # Inspect tables
    engine = create_engine(f"sqlite:///{db_file}")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected = [
        "dim_clients", "dim_accounts", "dim_time",
        "fact_transactions", "fact_events"
    ]
    for tbl in expected:
        assert tbl in tables, f"Expected table {tbl} in database"

    # Verify dim_time content
    df_time = pd.read_sql_table("dim_time", engine)
    assert not df_time.empty
