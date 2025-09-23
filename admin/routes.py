from flask import render_template, request, jsonify
from . import admin_bp
from .auth import token_required, admin_required, superadmin_required
from models import Usuario
from models import Mesa, Reserva, Cliente
from extensions import db
from werkzeug.security import generate_password_hash
import datetime

# ---------------------------
# RUTAS WEB (Frontend)
# ---------------------------

@admin_bp.route("/")
def index():
    """Login del panel admin"""
    return render_template("login.html")

@admin_bp.route("/dashboard")
@token_required
def dashboard(current_user):
    """Vista principal del admin"""
    return render_template("dashboard.html", usuario=current_user)

@admin_bp.route("/usuarios")
@token_required
@admin_required
def usuarios_view(current_user):
    return render_template("admin/usuarios.html")

@admin_bp.route("/mesas")
@token_required
@admin_required
def mesas_view(current_user):
    return render_template("admin/mesas.html")

@admin_bp.route("/reservas")
@token_required
@admin_required
def reservas_view(current_user):
    return render_template("admin/reservas.html")


# ---------------------------
# API: AUTENTICACIÓN
# ---------------------------

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login que devuelve un token JWT"""
    if request.method == "GET":
        return render_template("login.html")
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email y contraseña requeridos"}), 400

    usuario = Usuario.query.filter_by(email_Usuario=data["email"]).first()
    if not usuario or not usuario.check_password(data["password"]):
        return jsonify({"message": "Credenciales inválidas"}), 401

    token = usuario.generate_token()
    return jsonify({"token": token, "usuario": usuario.to_dict()})


# ---------------------------
# API: USUARIOS
# ---------------------------

@admin_bp.route("/usuarios", methods=["GET"])
@token_required
@admin_required
def listar_usuarios(current_user):
    usuarios = Usuario.query.all()
    return jsonify([u.to_dict() for u in usuarios])


@admin_bp.route("/usuarios", methods=["POST"])
@token_required
@superadmin_required
def crear_usuario(current_user):
    data = request.get_json()
    if not data or not data.get("nombre") or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Faltan campos obligatorios"}), 400

    if Usuario.query.filter_by(email_Usuario=data["email"]).first():
        return jsonify({"message": "El email ya está registrado"}), 400

    nuevo = Usuario(
        nombre_Usuario=data["nombre"],
        email_Usuario=data["email"],
        password_Usuario=data["password"],
        rol=data.get("rol", 0)
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201


@admin_bp.route("/usuarios/<int:id>", methods=["PUT"])
@token_required
@superadmin_required
def actualizar_usuario(current_user, id):
    usuario = Usuario.query.get_or_404(id)
    data = request.get_json()

    usuario.nombre_Usuario = data.get("nombre", usuario.nombre_Usuario)
    usuario.email_Usuario = data.get("email", usuario.email_Usuario)
    if data.get("password"):
        usuario.password_Usuario = generate_password_hash(data["password"])
    usuario.rol = data.get("rol", usuario.rol)
    usuario.is_active = data.get("is_active", usuario.is_active)

    db.session.commit()
    return jsonify(usuario.to_dict())


@admin_bp.route("/usuarios/<int:id>", methods=["DELETE"])
@token_required
@superadmin_required
def eliminar_usuario(current_user, id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"message": "Usuario eliminado"})


# ---------------------------
# API: MESAS
# ---------------------------

@admin_bp.route("/mesas", methods=["GET"])
@token_required
@admin_required
def listar_mesas(current_user):
    mesas = Mesa.query.all()
    return jsonify([{
        "id": m.id_Mesa,
        "numero": m.numero_Mesa,
        "capacidad": m.capacidad_Mesa,
        "estado": m.estado_Mesa
    } for m in mesas])


# ---------------------------
# API: RESERVAS
# ---------------------------

@admin_bp.route("/reservas", methods=["GET"])
@token_required
@admin_required
def listar_reservas(current_user):
    reservas = Reserva.query.all()
    return jsonify([{
        "id": r.id_Reserva,
        "cliente": r.cliente.nombre_Cliente,
        "mesa": r.mesa.numero_Mesa,
        "fecha": r.fecha_Reserva.isoformat(),
        "hora": r.hora_Reserva.strftime("%H:%M"),
        "personas": r.num_Personas,
        "estado": r.estado_Reserva
    } for r in reservas])

