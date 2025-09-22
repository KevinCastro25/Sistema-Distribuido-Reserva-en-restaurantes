from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask import render_template
from datetime import timedelta

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///reservasRest.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "supersecretkey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# ------------------ MODELO ------------------
class Usuario(db.Model):
    id_Usuario = db.Column(db.Integer, primary_key=True)
    nombre_Usuario = db.Column(db.String(100), nullable=False)
    email_Usuario = db.Column(db.String(100), unique=True, nullable=False)
    password_Usuario = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.Integer, default=0)

# ------------------ RUTAS ------------------

# Index
@app.route("/")
def index():
    return render_template("index.html")

# Dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# Registro
@app.route("/register", methods=["POST"])
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
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    usuario = Usuario.query.filter_by(email_Usuario=email).first()
    if not usuario or not check_password_hash(usuario.password_Usuario, password):
        return jsonify({"message": "Credenciales inválidas"}), 401

    token = create_access_token(identity={"id": usuario.id_Usuario, "rol": usuario.rol})
    return jsonify({"token": token}), 200

# Ruta protegida de back office (solo admins)
@app.route("/admin", methods=["GET"])
@jwt_required()
def admin_dashboard():
    identidad = get_jwt_identity()
    if identidad["rol"] != "admin":
        return jsonify({"message": "Acceso denegado. Solo admins."}), 403

    return jsonify({
        "message": "Bienvenido al Back Office 👑",
        "usuario": identidad
    }), 200

# ------------------ MAIN ------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
