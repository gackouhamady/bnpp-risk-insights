# --- Étape 1 : build de l’environnement
FROM python:3.10-slim AS builder

WORKDIR /app

# Copier requirements et installer en cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Étape 2 : copy du code
FROM python:3.10-slim

WORKDIR /app

# Copier l’environnement préinstallé
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copier le code source
COPY . .

# Exposer le port FastAPI
EXPOSE 8000

# Commande par défaut : démarre l’API
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
