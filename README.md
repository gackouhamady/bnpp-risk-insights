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

## 📅 Detailed 5-day working plan (+ 2 days buffer)



|                                                  Day                                                 | Key tasks                                                      |
| :--------------------------------------------------------------------------------------------------: | :------------------------------------------------------------- |
|                                               **Day 1**                                              | - **Init repo & env**: `git init` + `.gitignore` + Python venv |
| • `requirements.txt` (pandas, numpy, scikit-learn, sqlalchemy, mlflow, fastapi, uvicorn, streamlit…) |                                                                |

* **Data sampling**: simulated CSVs of client accounts, transactions, and KYC file (1,000 rows each) |
  \| **Day 2** | - **ETL & datamart** (`src/etl.py`):
  • Extraction CSV → Pandas → cleaning (formats, duplicates)
  • Loading into local SQLite or Postgres
  • Creation of fact tables (`transactions`, `events`) and dimensions (`clients`, `accounts`, `time`) |
  \| **Day 3** | - **Reporting & BI** (`src/reporting.py`):
  • Prototype Power BI/Tableau dashboard: key KPIs (transaction volume, active portfolio)
  • Automate CSV exports via Python/VBA for daily refresh |
  \| **Day 4** | - **Predictive modeling**:
  • `src/model_default.py` – Logistic Regression for payment default (features: average amount, frequency…)
  • `src/model_churn.py` – XGBoost to predict churn (features: tenure, average balance…)
  • Evaluation: AUC, confusion matrix, classification report |
  \| **Day 5** | - **Anomaly detection** (`src/anomaly.py`):
  • Isolation Forest on transaction amounts & frequencies
  • Visualization of outliers in Streamlit
* **Pipeline & MLOps** (`src/pipeline.py`):
  • Orchestration ETL → scoring → anomaly → JSON report generation
  • MLflow experiment tracking (params & metrics) |
  \| **Day 6** | - **Interface prototype** (`src/app.py`):
  • Local Streamlit to view dashboards, run scoring & anomaly
  • FastAPI exposing endpoints `/score_default`, `/detect_anomaly` |
  \| **Day 7** | - **Documentation & tests**:
  • `README.md` (installation, usage, Dataiku/GCP migration)
  • ER diagram in `docs/`
  • Pytest unit tests for each module
* **Packaging & delivery**:
  • Final `requirements.txt` (`pip freeze`)
  • Dockerfile (base `python:3.10`) for Streamlit + FastAPI app
  • Commit & push to GitHub + Cloud Run/Vertex AI deployment plan |

---

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