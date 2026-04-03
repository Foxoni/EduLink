# Image de base Python
FROM python:3.9-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Lancement de l'app
CMD ["python", "app.py"]