from flask import Blueprint

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route("/", methods=["GET"])
def reservas_home():
    return "Endpoint principal de reservas."
