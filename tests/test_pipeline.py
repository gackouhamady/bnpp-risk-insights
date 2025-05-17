# tests/test_pipeline.py

import subprocess
import json
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

def test_generate_data(repo_root):
    """
    Ensure synthetic data is generated successfully.
    """
    result = subprocess.run(
        ["python", "src/generate_data.py"],
        cwd=repo_root,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Data generation failed: {result.stderr}"
    raw_dir = repo_root / "data" / "raw"
    for fname in ["accounts.csv", "transactions.csv", "kyc.csv"]:
        assert (raw_dir / fname).exists(), f"{fname} not found in raw data dir"


def test_run_pipeline_and_report(repo_root):
    """
    Run the full pipeline script and check that a JSON report is created with expected sections.
    """
    result = subprocess.run(
        ["python", "src/pipeline.py"],
        cwd=repo_root,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Pipeline script failed: {result.stderr}"

    reports_dir = repo_root / "reports"
    assert reports_dir.exists(), "Reports directory not found"
    report_files = sorted(reports_dir.glob("report_*.json"))
    assert report_files, "No report JSON files created"

    # Validate content of latest report
    latest_report = report_files[-1]
    with open(latest_report, 'r') as f:
        report = json.load(f)

    # Expected top-level keys in report
    expected_keys = ["default_scoring", "churn_prediction", "anomaly_detection"]
    for key in expected_keys:
        assert key in report, f"Key '{key}' missing in report JSON"

    # Check metrics structure
    ds = report["default_scoring"]
    assert "auc" in ds and "accuracy" in ds, "Default scoring metrics incomplete"
    cp = report["churn_prediction"]
    assert "auc" in cp and "accuracy" in cp, "Churn prediction metrics incomplete"
    an = report["anomaly_detection"]
    assert isinstance(an, dict), "Anomaly detection section should be a dict"
