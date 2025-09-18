from flask import Blueprint

# Crear el blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Importar rutas para registrarlas en el blueprint
from . import routes
