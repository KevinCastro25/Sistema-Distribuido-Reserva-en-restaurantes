from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models import Usuario
from . import clientes_bp

# Vista principal (login/registro)
@clientes_bp.route("/")
def index():
    return render_template("index.html")

# Registro
@clientes_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    if Usuario.query.filter_by(email_Usuario=email).first():
        return jsonify({"message": "El usuario ya existe"}), 400

    hashed_pw = generate_password_hash(password)
    nuevo_usuario = Usuario(
        nombre_Usuario=nombre,
        email_Usuario=email,
        password_Usuario=hashed_pw
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"message": "Usuario creado con éxito"}), 201

# Login
@clientes_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    usuario = Usuario.query.filter_by(email_Usuario=email).first()
    if not usuario or not check_password_hash(usuario.password_Usuario, password):
        return jsonify({"message": "Credenciales inválidas"}), 401

    token = create_access_token(identity={"id": usuario.id_Usuario, "rol": usuario.rol})
    return jsonify({"token": token}), 200

# Dashboard simple del cliente
@clientes_bp.route("/dashboard")
@jwt_required()
def dashboard():
    identidad = get_jwt_identity()
    return jsonify({
        "message": "Bienvenido al Dashboard del cliente",
        "usuario": identidad
    }), 200