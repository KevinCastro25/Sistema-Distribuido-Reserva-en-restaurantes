from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/", methods=["GET"])
def admin_home():
    return "Endpoint principal de admin."
