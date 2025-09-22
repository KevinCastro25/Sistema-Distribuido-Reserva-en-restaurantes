from flask import Blueprint

reservas_bp = Blueprint(
    "reservas", __name__,
    template_folder="templates",
    static_folder="static"
)

from . import routes  # importa las rutas API
