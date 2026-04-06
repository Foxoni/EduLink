"""
Blueprint eleve — espace réservé aux élèves (id_role = 3).
Toute route de ce blueprint exige @role_required(3).
"""

from flask import Blueprint, render_template, session
from decorators import role_required

eleve_bp = Blueprint("eleve", __name__, url_prefix="/eleve",
                     template_folder="../../templates/eleve")


@eleve_bp.route("/dashboard")
@role_required(3)
def dashboard():
    return render_template("eleve/dashboard.html",
                           nom=session.get("nom"),
                           prenom=session.get("prenom"))
