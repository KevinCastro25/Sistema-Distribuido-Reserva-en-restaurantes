from flask import request, jsonify
from functools import wraps
import jwt

from . import admin_bp  # importa el blueprint aquí

# Decorador para proteger rutas solo para admins
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from app import Usuario  # importa dentro de la función para evitar circular import
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token faltante"}), 403
        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, "miclaveultrasecreta", algorithms=["HS256"])
            usuario = Usuario.query.get(data["id_Usuario"])
            if not usuario or usuario.rol != 1:
                return jsonify({"message": "Acceso denegado: solo admins"}), 403
        except Exception as e:
            return jsonify({"message": "Token inválido", "error": str(e)}), 403
        return f(*args, **kwargs)
    return decorated

# RUTA DE PRUEBA
@admin_bp.route("/", methods=["GET"])
def admin_home():
    return jsonify({"message": "Admin Home funcionando"})

# Listar reservas
@admin_bp.route("/reservas", methods=["GET"])
@admin_required
def ver_reservas():
    from app import Reserva
    reservas = Reserva.query.all()
    resultado = []
    for r in reservas:
        resultado.append({
            "id": r.id_Reserva,
            "usuario": r.id_Usuario,
            "mesa": r.id_Mesa,
            "fecha": str(r.fecha_Reserva),
            "hora": str(r.hora_Reserva),
            "personas": r.num_Personas,
            "estado": r.estado_Reserva
        })
    return jsonify(resultado)
