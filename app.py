from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def accueil():
    # Données du professeur (plus tard ça viendra de MySQL)
    prof = {
        "prenom": "Lucie",
        "nom": "Petit"
    }

    # Les cartes du dashboard
    dashboard = [
        {"title": "Créer un projet",                  "url": "/projets"},
        {"title": "Consulter mes classes",             "url": "/classes"},
        {"title": "Créer une évaluation",              "url": "/evaluations"},
        {"title": "Attribuer / modifier les notes",    "url": "/notes"},
        {"title": "Ajouter des commentaires",          "url": "/commentaires"},
        {"title": "Mettre des élèves absents",         "url": "/absences"},
        {"title": "Consulter mon emploi du temps",     "url": "/edt"},
    ]

    # Récupérer la date actuelle et formater en français
    now = datetime.now()
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois = ["janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    date_fr = f"{jours[now.weekday()]} {now.day} {mois[now.month-1]} {now.year}"

    return render_template('prof/index.html', prof=prof, dashboard=dashboard, date_fr=date_fr)

@app.route('/projets')
def projets():
    # Exemple de données projets (tu pourras récupérer depuis MySQL plus tard)
    liste_projets = [
        {"nom": "Projet A", "statut": "En cours"},
        {"nom": "Projet B", "statut": "Terminé"},
        {"nom": "Projet C", "statut": "À démarrer"},
    ]
    return render_template('prof/projets.html', projets=liste_projets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)