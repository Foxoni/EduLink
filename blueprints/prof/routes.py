"""
Blueprint prof — espace réservé aux professeurs (id_role = 2).
Toute route de ce blueprint exige @role_required(2).
"""

from flask import Blueprint, render_template, session
from decorators import role_required

prof_bp = Blueprint("prof", __name__, url_prefix="/prof",
                    template_folder="../../templates/prof")


@prof_bp.route("/dashboard")
@role_required(2)
def dashboard():
    return render_template("prof/dashboard.html",
                           nom=session.get("nom"),
                           prenom=session.get("prenom"))
