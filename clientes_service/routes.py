from flask import Blueprint, jsonify

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route("/", methods=["GET"])
def clientes_home():
    return "Endpoint principal de clientes."


# Endpoint para obtener datos de un cliente por ID (ejemplo)
@clientes_bp.route("/<int:cliente_id>", methods=["GET"])
def get_cliente(cliente_id):
    # Ejemplo de datos
    ejemplo_cliente = {
        1: {"id": 1, "nombre": "Juan", "email": "juan@email.com"},
        2: {"id": 2, "nombre": "Ana", "email": "ana@email.com"}
    }
    cliente = ejemplo_cliente.get(cliente_id)
    if cliente:
        return jsonify(cliente)
    else:
        return jsonify({"error": "Cliente no encontrado"}), 404
