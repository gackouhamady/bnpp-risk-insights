# tests/test_models.py

import subprocess
import joblib
import xgboost as xgb
from pathlib import Path
import pytest

# ─── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def repo_root():
    """
    Determine the repository root directory.
    """
    return Path(__file__).resolve().parent.parent

@pytest.fixture(scope="module")
def models_dir(repo_root):
    """
    Ensure the models directory exists.
    """
    d = repo_root / "models"
    d.mkdir(parents=True, exist_ok=True)
    return d

# ─── Tests ─────────────────────────────────────────────────────────────────────
def test_default_model_training(repo_root, models_dir):
    """
    Run the default scoring script and verify the model file is created and loadable.
    """
    model_path = models_dir / "logreg_default.pkl"
    # Remove existing model if present
    if model_path.exists():
        model_path.unlink()

    # Execute the training script
    result = subprocess.run(
        ["python", "src/model_default.py"],
        cwd=repo_root,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Default model script failed: {result.stderr}"

    # Check that model file was created
    assert model_path.exists(), "Default model file not created"

    # Load and inspect the model
    model = joblib.load(str(model_path))
    assert hasattr(model, "predict"), "Loaded default model has no predict method"
    assert hasattr(model, "predict_proba"), "Loaded default model has no predict_proba method"


def test_churn_model_training(repo_root, models_dir):
    """
    Run the churn prediction script and verify the XGBoost model file is created and loadable.
    """
    churn_path = models_dir / "xgb_churn.json"
    # Remove existing model if present
    if churn_path.exists():
        churn_path.unlink()

    # Execute the training script
    result = subprocess.run(
        ["python", "src/model_churn.py"],
        cwd=repo_root,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Churn model script failed: {result.stderr}"

    # Check that model file was created
    assert churn_path.exists(), "Churn model file not created"

    # Load and inspect the model
    booster = xgb.Booster()
    booster.load_model(str(churn_path))
    assert isinstance(booster, xgb.Booster), "Loaded churn model is not an XGBoost Booster"