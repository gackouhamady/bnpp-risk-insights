# 🚀 DataHub Risk & Customer Insights

**Prototype developed for the BNP Paribas Data Science CoE:**

* Data ingestion & preparation
* Analytics datamart (star schema)
* Interactive reporting & dashboards
* Predictive modeling (default scoring & churn prediction)
* Transaction anomaly detection
* Lightweight MLOps pipeline (scripts + MLflow)
* REST API (FastAPI) & Streamlit UI
* Docker container

---

## 📊 Model Performance Summary

| Model                | AUC    | Precision (0 / 1) | Recall (0 / 1) | F1-score (0 / 1) | Accuracy |
| -------------------- | ------ | ----------------- | -------------- | ---------------- | -------- |
| **Default Scoring**  | 0.9981 | 0.97 / 0.97       | 0.99 / 0.89    | 0.98 / 0.93      | 0.97     |
| **Churn Prediction** | 0.9167 | 0.96 / 1.00       | 1.00 / 0.83    | 0.98 / 0.91      | 0.97     |

> **Default Scoring** (Logistic Regression)
>
> * AUC: 0.9981 (almost perfect separation)
> * Accuracy: 97% (192 samples)

> **Churn Prediction** (XGBoost)
>
> * AUC: 0.9167 (excellent churn vs. retention discrimination)
> * Accuracy: 97% (30 samples)

---

## 📅 Detailed Day-by-Day Plan

| Day | Deliverables                                                                                                                                                     |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | - Repo & venv initialization, `.gitignore`  <br> - `requirements.txt`  <br> - Generate 1,000 synthetic rows (accounts, transactions, KYC)                        |
| 2   | - ETL & datamart (`src/etl.py`): extract raw CSVs, clean data, create star schema, load into SQLite/PostgreSQL                                                   |
| 3   | - Reporting & BI (`src/reporting.py`): timestamped CSV exports & Power BI/Tableau prototype  <br> - Daily refresh script                                         |
| 4   | - Default scoring (`src/model_default.py`)  <br> - Churn prediction (`src/model_churn.py`)  <br> - AUC, confusion matrix, classification report                  |
| 5   | - Anomaly detection (`src/anomaly.py`): Isolation Forest & Streamlit UI  <br> - Partial orchestration                                                            |
| 6   | - Full pipeline (`src/pipeline.py`): ETL → default & churn scoring → anomalies → MLflow → JSON report  <br> - FastAPI endpoints (`src/app.py`)                   |
| 7   | - Write `README.md`  <br> - ER diagram (`docs/datamart_schema.png`)  <br> - Unit tests (Pytest)  <br> - `Dockerfile` (Python 3.10)  <br> - Cloud deployment plan |

---

## ⚙️ Repository Structure

```bash
bnpp-risk-insights/
├── data/
│   ├── raw/                 # synthetic CSVs: accounts, transactions, KYC
│   ├── processed/           # SQLite datamart (`risk_insights.db`)
│   └── exports/             # timestamped CSVs for BI
├── docs/
│   ├── datamart_schema.png  # star schema ER diagram
│   └── anomaly_ui.png       # Streamlit anomaly detection screenshot
├── models/
│   ├── logreg_default.pkl   # default scoring model
│   └── xgb_churn.json       # churn prediction model
├── reports/
│   └── report_YYYYMMDD_HHMMSS.json  # JSON reports per run
├── src/
│   ├── generate_data.py     # synthetic data generator
│   ├── etl.py               # extract, transform, load
│   ├── reporting.py         # CSV exports & BI prep
│   ├── model_default.py     # logistic regression scoring
│   ├── model_churn.py       # XGBoost churn prediction
│   ├── anomaly.py           # Isolation Forest + Streamlit UI
│   ├── pipeline.py          # orchestration + MLflow + JSON report
│   └── app.py               # FastAPI application
├── tests/                   # Pytest unit tests
├── Dockerfile               # multi-stage Python 3.10 container
├── requirements.txt         # Python dependencies
└── README.md                # project documentation
```

---

## 🛠 Installation & Usage

1. **Clone & prepare venv**

   ```bash
   git clone <repo>
   python -m venv venv
   # Windows
   .\\venv\\Scripts\\Activate.ps1
   ```
2. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. **Generate sample data**

   ```bash
   python src/generate_data.py
   ```
4. **Build the datamart**

   ```bash
   python src/etl.py
   ```
5. **Export for BI**

   ```bash
   python src/reporting.py
   ```
6. **Train models**

   ```bash
   python src/model_default.py
   python src/model_churn.py
   ```
7. **Run the anomaly UI**

   ```bash
   streamlit run src/anomaly.py
   ```

   <img src="docs/anomaly.png" alt="Streamlit Anomaly UI" width="700"/>
8. **Orchestrate & generate report**

   ```bash
   python src/pipeline.py
   ```
9. **Start the API**

   ```bash
   python -m uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
   ```

   > Access the docs at `http://localhost:8000/docs`
10. **Run unit tests**

    ```bash
    pytest --maxfail=1 -q
    ```
11. **Docker**

    ```bash
    docker build -t risk-insights:latest .
    docker run -p 8000:8000 risk-insights:latest
    ```

---

## 🔒 Governance & Ethics

* Synthetic data only → no real PII
* GDPR-compliant: anonymization & privacy by design
* Transparent, versioned code with unit tests
* Ready for industrialization (Dataiku / GCP)

*An industrial-grade blueprint for risk & customer analytics in banking.*
