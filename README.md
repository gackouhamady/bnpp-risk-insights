# 🚀 Project Objective

Prototype a **DataHub Risk & Customer Insights** for BNP Paribas CoE Data Science, covering:

* **Data ingestion & preparation** (accounts, transactions, KYC) in Python & SQL
* **Building a Risk & Customer Analytics datamart** (star schema)
* **Interactive reporting & dashboards** with Power BI or Tableau
* **Predictive modeling**: default scoring (Logistic Regression) and churn (XGBoost)
* **Transaction anomaly detection** (Isolation Forest)
* **Lightweight MLOps pipeline** (Airflow or batch scripts + MLflow)
* **Documentation & best practices** (versioning, testing, GDPR/anonymization)

---

## 📅 Detailed 5-Day Working Plan (+2 Days Buffer)

| **Day**       | **Key Tasks** |
|---------------|---------------|
| **Day 1**      | - **Init repo & env**: `git init` + `.gitignore` + Python venv  <br> - `requirements.txt` (pandas, numpy, scikit-learn, sqlalchemy, mlflow, fastapi, uvicorn, streamlit…)  <br> - **Data sampling**: simulated CSVs of client accounts, transactions, and KYC file (1,000 rows each) |
| **Day 2**      | - **ETL & datamart** (`src/etl.py`):  <br>  • Extraction CSV → Pandas → cleaning (formats, duplicates)  <br>  • Loading into local SQLite or Postgres  <br>  • Creation of fact tables (`transactions`, `events`) and dimensions (`clients`, `accounts`, `time`) |
| **Day 3**      | - **Reporting & BI** (`src/reporting.py`):  <br>  • Prototype Power BI/Tableau dashboard: key KPIs (transaction volume, active portfolio)  <br>  • Automate CSV exports via Python/VBA for daily refresh |
| **Day 4**      | - **Predictive modeling**:  <br>  • `src/model_default.py`: Logistic Regression for payment default (features: average amount, frequency…)  <br>  • `src/model_churn.py`: XGBoost to predict churn (features: tenure, average balance…)  <br>  • Evaluation: AUC, confusion matrix, classification report |
| **Day 5**      | - **Anomaly detection** (`src/anomaly.py`):  <br>  • Isolation Forest on transaction amounts & frequencies  <br>  • Visualization of outliers in Streamlit  <br> - **Pipeline & MLOps** (`src/pipeline.py`):  <br>  • Orchestration ETL → scoring → anomaly → JSON report generation  <br>  • MLflow experiment tracking (params & metrics) |
| **Day 6** *(Buffer)* | - **Interface prototype** (`src/app.py`):  <br>  • Local Streamlit to view dashboards, run scoring & anomaly  <br>  • FastAPI exposing endpoints `/score_default`, `/detect_anomaly` |
| **Day 7** *(Buffer)* | - **Documentation & tests**:  <br>  • `README.md` (installation, usage, Dataiku/GCP migration)  <br>  • ER diagram in `docs/`  <br>  • Pytest unit tests for each module  <br> - **Packaging & delivery**:  <br>  • Final `requirements.txt` (`pip freeze`)  <br>  • Dockerfile (base `python:3.10`) for Streamlit + FastAPI app  <br>  • Commit & push to GitHub + Cloud Run/Vertex AI deployment plan |

## ⚙️ Final Git structure

```bash
bnpp-risk-insights/
├── data/
│   ├── raw/                       # simulated accounts, transactions, KYC CSVs
│   └── processed/                 # cleansed tables
├── docs/
│   └── datamart_schema.png        # star schema diagram
├── src/
│   ├── etl.py                     # extraction, cleaning, loading
│   ├── reporting.py               # CSV exports & BI templates
│   ├── model_default.py           # default scoring (Logistic Regression)
│   ├── model_churn.py             # churn (XGBoost)
│   ├── anomaly.py                 # Isolation Forest
│   ├── pipeline.py                # orchestration + MLflow
│   └── app.py                     # Streamlit + FastAPI
├── tests/
│   ├── test_etl.py
│   ├── test_reporting.py
│   ├── test_models.py
│   └── test_pipeline.py
├── Dockerfile
├── README.md
├── requirements.txt
└── .gitignore
```



## Architecture summary  

``` text

1. Data Sources
   ├─ Client accounts (CSV)
   ├─ Transactions (CSV)
   └─ KYC (CSV)

2. Ingestion & Preparation (ETL)
   ├─ Extraction (pandas)
   ├─ Cleaning (formats, duplicates, GDPR)
   └─ Loading (SQLAlchemy → SQLite/Postgres)

3. Datamart (star schema)
   ├─ Fact tables
   │   ├─ transactions
   │   └─ events
   └─ Dimension tables
       ├─ clients
       ├─ accounts
       └─ time

4. Storage & Traceability
   ├─ Optimized SQL database
   └─ MLflow (tracking runs: parameters, metrics, artifacts)

5. Analytical Modules
   ├─ Default scoring (logistic regression)
   ├─ Churn prediction (XGBoost)
   └─ Anomaly detection (Isolation Forest)

6. MLOps Orchestration
   ├─ Airflow or batch scripts
   └─ Pipeline ETL → scoring → anomaly → JSON reports

7. Interfaces
   ├─ Streamlit (dashboards & manual execution)
   └─ FastAPI (endpoints `/score_default` & `/detect_anomaly`)

8. Containerization & Deployment
   ├─ Docker (Python 3.10)
   └─ Cloud Run / Vertex AI (auto-scaling, monitoring)

9. Quality & Governance
   ├─ Unit tests (Pytest)
   ├─ Documentation (README, ER diagram)
   └─ Git conventions and code reviews

```
