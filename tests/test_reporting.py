# tests/test_reporting.py

import subprocess
import pandas as pd
from pathlib import Path
import pytest

# ─── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def repo_root():
    """
    Repository root directory.
    """
    return Path(__file__).resolve().parent.parent

# ─── Tests ─────────────────────────────────────────────────────────────────────

def test_run_reporting_pipeline(repo_root):
    """
    Run data generation, ETL, and reporting scripts, then verify CSV exports exist and contain data.
    """
    cwd = repo_root

    # 1) Generate synthetic data
    result = subprocess.run(
        ["python", "src/generate_data.py"],
        cwd=cwd,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Data generation failed: {result.stderr}"

    # 2) Build datamart via ETL
    result = subprocess.run(
        ["python", "src/etl.py"],
        cwd=cwd,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"ETL script failed: {result.stderr}"

    # 3) Run reporting
    result = subprocess.run(
        ["python", "src/reporting.py"],
        cwd=cwd,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Reporting script failed: {result.stderr}"

    # 4) Check exports directory and CSV files
    exports_dir = repo_root / "data" / "exports"
    assert exports_dir.exists(), "Exports directory not found"
    csv_files = list(exports_dir.glob("*.csv"))
    assert csv_files, "No CSV files exported"

    # 5) Validate each CSV has content and expected columns
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        # Ensure file is not empty
        assert not df.empty, f"Exported CSV {csv_file.name} is empty"
        # Check basic structure: at least 2 columns
        assert df.shape[1] >= 2, f"Exported CSV {csv_file.name} has unexpected format"
