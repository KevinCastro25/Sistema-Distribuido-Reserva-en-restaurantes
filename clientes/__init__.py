from flask import Blueprint

clientes_bp = Blueprint(
    "clientes", __name__,
    template_folder="templates", 
    static_folder="static"
)

# Importamos las rutas después de definir el blueprint
from . import routes
