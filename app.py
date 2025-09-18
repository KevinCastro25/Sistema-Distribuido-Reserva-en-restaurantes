from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})

app.config["SECRET_KEY"] = "miclaveultrasecreta"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///reservasRest.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------
# MODELO USUARIO
# -------------------
class Usuario(db.Model):
    __tablename__ = "Usuario"
    id_Usuario = db.Column(db.Integer, primary_key=True)
    nombre_Usuario = db.Column(db.String(100), nullable=False)
    email_Usuario = db.Column(db.String(100), unique=True, nullable=False)
    password_Usuario = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.Integer, default=0)

# -------------------
# ENDPOINTS
# -------------------

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    if not nombre or not email or not password:
        return jsonify({"message": "Faltan datos"}), 400

    if Usuario.query.filter_by(email_Usuario=email).first():
        return jsonify({"message": "El correo ya está registrado"}), 400

    hashed_pw = generate_password_hash(password)
    nuevo_usuario = Usuario(
        nombre_Usuario=nombre,
        email_Usuario=email,
        password_Usuario=hashed_pw
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"message": "Usuario registrado con éxito"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    usuario = Usuario.query.filter_by(email_Usuario=email).first()
    if not usuario or not check_password_hash(usuario.password_Usuario, password):
        return jsonify({"message": "Credenciales inválidas"}), 401

    token = jwt.encode(
        {
            "id_Usuario": usuario.id_Usuario,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        },
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )
    return jsonify({"token": token})


@app.route("/perfil", methods=["GET"])
def perfil():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Token faltante"}), 403

    try:
        token = token.split(" ")[1]  # formato: "Bearer <token>"
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        usuario = Usuario.query.get(data["id_Usuario"])
        if not usuario:
            return jsonify({"message": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"message": "Token inválido", "error": str(e)}), 403

    return jsonify({
        "id": usuario.id_Usuario,
        "nombre": usuario.nombre_Usuario,
        "email": usuario.email_Usuario,
        "rol": usuario.rol
    })


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)