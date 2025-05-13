# 🚀 Objectif du projet
Prototyper un **DataHub Risk & Customer Insights** pour BNP Paribas CoE Data Science, couvrant :

- **Ingestion & préparation** de données (comptes, transactions, KYC) en Python & SQL  
- **Construction d’un datamart** Risk & Customer Analytics (star schema)  
- **Reporting & dashboards** interactifs avec Power BI ou Tableau  
- **Modélisation prédictive** : scoring défaut (Logistic Regression) et churn (XGBoost)  
- **Détection d’anomalies** transactions (Isolation Forest)  
- **Pipeline MLOps léger** (Airflow ou scripts batch + MLflow)  
- **Documentation & bonnes pratiques** (versioning, tests, GDPR/anonymisation)  

---

## 📅 Planning détaillé sur 5 jours ouvrés (+ 2 jours de buffer)

| Jour   | Tâches clés                                                                                                                                                                                                  |
|:------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Jour 1** | - **Init repo & env** : `git init` + `.gitignore` + venv Python  
  • `requirements.txt` (pandas, numpy, scikit-learn, sqlalchemy, mlflow, fastapi, uvicorn, streamlit…)  
  - **Data sampling** : CSV simulés de comptes clients, transactions et fichier KYC (1 000 lignes chacun) |
| **Jour 2** | - **ETL & datamart** (`src/etl.py`) :  
  • Extraction CSV → Pandas → nettoyage (formats, doublons)  
  • Chargement dans SQLite ou Postgres local  
  • Création des tables fact (`transactions`, `events`) et dimensions (`clients`, `comptes`, `temps`) |
| **Jour 3** | - **Reporting & BI** (`src/reporting.py`) :  
  • Prototype de dashboard Power BI/Tableau : KPIs clés (volume transactions, portefeuille actif)  
  • Automatisation d’exports CSV via Python/VBA pour refresh quotidien |
| **Jour 4** | - **Modélisation prédictive** :  
  • `src/model_default.py` – Logistic Regression pour défaut de paiement (features : montant moyen, fréquence…)  
  • `src/model_churn.py` – XGBoost pour prédire churn (features : ancienneté, solde moyen…)  
  • Évaluation : AUC, confusion matrix, rapport classification |
| **Jour 5** | - **Détection d’anomalies** (`src/anomaly.py`) :  
  • Isolation Forest sur montants & fréquences de transaction  
  • Visualisation des outliers dans Streamlit  
  - **Pipeline & MLOps** (`src/pipeline.py`) :  
  • Orchestration ETL → scoring → anomaly → génération de rapport JSON  
  • Tracking d’expériences MLflow (params & metrics) |
| **Jour 6** | - **Prototype d’interface** (`src/app.py`) :  
  • Streamlit local pour visualiser dashboards, lancer scoring & anomaly  
  • FastAPI exposant endpoints `/score_default`, `/detect_anomaly` |
| **Jour 7** | - **Documentation & tests** :  
  • `README.md` (installation, usage, migration Dataiku/GCP)  
  • Diagramme ER dans `docs/`  
  • Tests unitaires pytest pour chaque module  
  - **Packaging & livraison** :  
  • `requirements.txt` final (`pip freeze`)  
  • Dockerfile (base `python:3.10`) pour app Streamlit + FastAPI  
  • Commit & push sur GitHub + plan de déploiement Cloud Run/Vertex AI |

---

## ⚙️ Structure Git finale

```bash
bnpp-risk-insights/
├── data/
│   ├── raw/                       # CSV simulés comptes, transactions, KYC
│   └── processed/                 # tables cleansed
├── docs/
│   └── datamart_schema.png        # diagramme star schema
├── src/
│   ├── etl.py                     # extraction, nettoyage, chargement
│   ├── reporting.py               # exports CSV & templates BI
│   ├── model_default.py           # scoring défaut (Logistic Regression)
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
