"""
src/generate_data.py

This script generates three synthetic datasets for the “DataHub Risk & Customer Insights” prototype:
  - data/raw/accounts.csv     : client accounts (account_id, client_id, account_type, opened_date)
  - data/raw/transactions.csv : transaction history (transaction_id, account_id, amount, transaction_date, transaction_type)
  - data/raw/kyc.csv          : client KYC data (client_id, name, birthdate, country)

Purpose:
  • Provide a realistic testbed for the ETL pipeline, datamart population, and training of
    predictive models (default scoring, churn prediction) and anomaly detection.
  • Ensure reproducibility and consistency of test data throughout development and testing.
"""

import pandas as pd
import numpy as np
from faker import Faker # type: ignore

fake = Faker()
Faker.seed(42)
n = 1000

# Client accounts
accounts = pd.DataFrame({
    "account_id": range(1, n+1),
    "client_id": np.random.randint(1, n//10, size=n),
    "account_type": np.random.choice(["checking","savings"], size=n),
    "opened_date": [fake.date_between(start_date='-5y', end_date='today') for _ in range(n)]
})

# Transactions
transactions = pd.DataFrame({
    "transaction_id": range(1, n+1),
    "account_id": np.random.choice(accounts.account_id, size=n),
    "amount": np.round(np.random.exponential(scale=200, size=n),2),
    "transaction_date": [fake.date_time_between(start_date='-1y', end_date='now') for _ in range(n)],
    "transaction_type": np.random.choice(["debit","credit"], size=n)
})

# KYC
kyc = pd.DataFrame({
    "client_id": accounts.client_id.unique(),
    "name": [fake.name() for _ in accounts.client_id.unique()],
    "birthdate": [fake.date_of_birth(minimum_age=18, maximum_age=90) for _ in accounts.client_id.unique()],
    "country": [fake.country() for _ in accounts.client_id.unique()]
})

# Sauvegarde en CSV
accounts.to_csv("data/raw/accounts.csv", index=False)
transactions.to_csv("data/raw/transactions.csv", index=False)
kyc.to_csv("data/raw/kyc.csv", index=False)
print("CSV files generated in data/raw/")
