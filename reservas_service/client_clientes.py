import requests
from flask import Blueprint

consultar_clientes_bp = Blueprint('consultar_clientes', __name__)

@consultar_clientes_bp.route('/consultar_cliente/<int:cliente_id>', methods=['GET'])
def consultar_cliente(cliente_id):
    try:
        response = requests.get(f'http://clientes_service:5001/clientes/{cliente_id}')
        return response.text, response.status_code
    except Exception as e:
        return f'Error al consultar microservicio de clientes: {e}', 500
