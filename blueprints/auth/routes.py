"""
Blueprint auth — page de connexion commune et déconnexion.

Sécurité :
- Requête SQL paramétrée (aucune concaténation)
- Vérification bcrypt du mot de passe haché
- Token CSRF validé par Flask-WTF sur le POST
- Session régénérée après connexion (prévention fixation de session)
"""

import bcrypt
from flask import (
    Blueprint, render_template, request,
    session, redirect, url_for, flash,
)
from db import get_db

auth_bp = Blueprint("auth", __name__, template_folder="../../templates")

# IDs de rôles (doivent correspondre à la table Roles)
ROLE_ADMIN = 1
ROLE_PROF = 2
ROLE_ELEVE = 3

_REDIRECT_MAP = {
    ROLE_ADMIN: "admin.dashboard",
    ROLE_PROF:  "prof.dashboard",
    ROLE_ELEVE: "eleve.dashboard",
}


@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return _redirect_to_dashboard(session["role_id"])

    error = None

    if request.method == "POST":
        compte = request.form.get("compte", "").strip()
        mdp = request.form.get("mdp", "")

        if not compte or not mdp:
            error = "Veuillez remplir tous les champs."
        else:
            db = get_db()
            cur = db.cursor(dictionary=True)
            # Requête paramétrée — aucune concaténation SQL possible
            cur.execute(
                "SELECT id_user, id_role, mdp, nom, prenom "
                "FROM Utilisateurs WHERE compte = %s",
                (compte,),
            )
            user = cur.fetchone()
            cur.close()

            if user and bcrypt.checkpw(mdp.encode(), user["mdp"].encode()):
                # Régénération de session pour prévenir la fixation de session
                session.clear()
                session["user_id"] = user["id_user"]
                session["role_id"] = user["id_role"]
                session["nom"] = user["nom"]
                session["prenom"] = user["prenom"]
                session.permanent = True  # applique PERMANENT_SESSION_LIFETIME
                return _redirect_to_dashboard(user["id_role"])
            else:
                # Message volontairement générique (pas de fuite d'info)
                error = "Identifiant ou mot de passe incorrect."

    return render_template("login.html", error=error)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Vous avez été déconnecté.")
    return redirect(url_for("auth.login"))


def _redirect_to_dashboard(role_id):
    endpoint = _REDIRECT_MAP.get(role_id)
    if endpoint:
        return redirect(url_for(endpoint))
    return redirect(url_for("auth.login"))
