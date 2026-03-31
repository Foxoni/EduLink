from flask import Flask, render_template

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

    return render_template('prof/index.html', prof=prof, dashboard=dashboard)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)