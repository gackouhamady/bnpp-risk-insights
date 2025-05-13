# Plan d'action pour le prototype DataHub Risk & Customer Insights

Ce document décrit les tâches à réaliser chaque jour pour finaliser le prototype en une semaine.

---

## Jour 1 – Initialisation

* `git init` : création du dépôt Git
* Configuration de l’environnement Python (venv)
* Création du fichier `requirements.txt` avec les dépendances principales (pandas, numpy, scikit-learn, sqlalchemy, mlflow, fastapi, streamlit…)
* Génération des jeux de données simulés (CSV pour comptes, transactions, KYC)

## Jour 2 – ETL & Datamart

* Développement du script `src/etl.py` :

  * Extraction des CSV avec pandas
  * Nettoyage (formats, doublons, valeurs manquantes)
  * Chargement dans SQLite/Postgres via SQLAlchemy
* Conception du schéma en étoile :

  * Création des tables de faits (`transactions`, `events`)
  * Création des tables de dimensions (`clients`, `accounts`, `time`)

## Jour 3 – Reporting & Dashboard

* Écriture du module `src/reporting.py` :

  * Génération des exports CSV automatisés pour le dashboard
  * Mise en place d’un prototype de connexion à Power BI ou Tableau
* Tests de rafraîchissement quotidien des données

## Jour 4 – Modélisation prédictive

* Implémentation du scoring défaut (`src/model_default.py`) :

  * Régression logistique, sélection des features (montant moyen, fréquence…)
  * Évaluation (AUC, matrice de confusion)
* Implémentation du churn (`src/model_churn.py`) :

  * XGBoost, features (ancienneté, solde moyen…)
  * Rapport de classification

## Jour 5 – Détection d’anomalies

* Développement de `src/anomaly.py` :

  * Isolation Forest sur montants et fréquences
  * Calcul des scores d’anomalie
* Création d’une interface Streamlit pour visualiser les outliers

## Jour 6 – Orchestration & API

* Élaboration du pipeline dans `src/pipeline.py` :

  * Orchestration ETL → scoring → anomalie → génération de rapports JSON
  * Intégration de MLflow pour le tracking
* Développement de l’API FastAPI (`src/app.py`) :

  * Endpoints `/score_default` et `/detect_anomaly`

## Jour 7 – Finalisation & Livraison

* Rédaction du `README.md` (installation, usage, migration Dataiku/GCP)
* Création du diagramme ER dans `docs/datamart_schema.png`
* Écriture des tests unitaires (Pytest) pour chaque module
* Rédaction de la Dockerfile (base Python 3.10)
* Préparation du plan de déploiement sur Cloud Run / Vertex AI

---

*Fin du plan d’action*
