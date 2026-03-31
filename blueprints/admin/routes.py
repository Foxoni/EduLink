"""
Blueprint admin — espace réservé aux administrateurs (id_role = 1).
Toute route de ce blueprint exige @role_required(1).
"""

from flask import Blueprint, render_template, session
from decorators import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin",
                     template_folder="../../templates/admin")


@admin_bp.route("/dashboard")
@role_required(1)
def dashboard():
    return render_template("admin/dashboard.html",
                           nom=session.get("nom"),
                           prenom=session.get("prenom"))
