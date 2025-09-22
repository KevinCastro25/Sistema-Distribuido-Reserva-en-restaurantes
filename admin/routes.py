from flask import Blueprint, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

admin_bp = Blueprint(
    "admin", __name__,
    template_folder="templates",
    static_folder="static"
)

# Dashboard de administrador
@admin_bp.route("/")
@jwt_required()
def admin_dashboard():
    identidad = get_jwt_identity()
    if identidad["rol"] != "admin":
        return jsonify({"message": "Acceso denegado. Solo admins."}), 403

    return render_template("dashboard.html")
