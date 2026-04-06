# On part d'une version légère de Python
FROM python:3.9-slim

# On définit le dossier de travail dans le container
WORKDIR /app

# On copie le fichier des dépendances
COPY requirements.txt .

# On installe les outils nécessaires (Flask, MySQL, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# On copie tout le reste de ton code (app.py, templates, etc.)
COPY . .

# On lance le site
CMD ["python", "app.py"]