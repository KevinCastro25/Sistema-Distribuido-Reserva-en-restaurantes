from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuración
app.config["SECRET_KEY"] = "miclaveultrasecreta"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///reservasRest.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------
# MODELO USUARIO (Mejorado)
# -------------------
class Usuario(db.Model):
    __tablename__ = "Usuario"
    id_Usuario = db.Column(db.Integer, primary_key=True)
    nombre_Usuario = db.Column(db.String(100), nullable=False)
    email_Usuario = db.Column(db.String(100), unique=True, nullable=False)
    password_Usuario = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.Integer, default=0)  # 0=usuario, 1=admin, 2=superadmin
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def check_password(self, password):
        return check_password_hash(self.password_Usuario, password)

    def generate_token(self):
        payload = {
            'id_Usuario': self.id_Usuario,
            'email': self.email_Usuario,
            'rol': self.rol,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

    def to_dict(self):
        return {
            'id': self.id_Usuario,
            'nombre': self.nombre_Usuario,
            'email': self.email_Usuario,
            'rol': self.rol,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def is_admin(self):
        return self.rol >= 1

# -------------------
# DECORADORES DE AUTENTICACIÓN
# -------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'message': 'Token faltante'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Usuario.query.get(data['id_Usuario'])
            if not current_user or not current_user.is_active:
                return jsonify({'message': 'Usuario inválido'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'message': 'Permisos de administrador requeridos'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

# -------------------
# RUTAS WEB (Templates)
# -------------------
@app.route("/")
def index():
    return render_template('login.html')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route("/admin")
def admin_panel():
    return render_template('admin/usuarios.html')

# -------------------
# ENDPOINTS API
# -------------------
@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        nombre = data.get("nombre", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        rol = data.get("rol", 0)

        # Validaciones básicas
        if not nombre or not email or not password:
            return jsonify({"message": "Todos los campos son requeridos"}), 400

        if len(password) < 6:
            return jsonify({"message": "La contraseña debe tener al menos 6 caracteres"}), 400

        if Usuario.query.filter_by(email_Usuario=email).first():
            return jsonify({"message": "El correo ya está registrado"}), 400

        # Crear usuario
        hashed_pw = generate_password_hash(password)
        nuevo_usuario = Usuario(
            nombre_Usuario=nombre,
            email_Usuario=email,
            password_Usuario=hashed_pw,
            rol=rol
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({
            "message": "Usuario registrado con éxito",
            "user": nuevo_usuario.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error interno", "error": str(e)}), 500

@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"message": "Email y contraseña son requeridos"}), 400

        usuario = Usuario.query.filter_by(email_Usuario=email).first()
        
        if not usuario or not usuario.check_password(password):
            return jsonify({"message": "Credenciales inválidas"}), 401

        if not usuario.is_active:
            return jsonify({"message": "Cuenta inactiva"}), 401

        token = usuario.generate_token()
        
        return jsonify({
            "message": "Login exitoso",
            "token": token,
            "user": usuario.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"message": "Error interno", "error": str(e)}), 500

@app.route("/api/perfil", methods=["GET"])
@token_required
def perfil(current_user):
    return jsonify({
        "message": "Perfil obtenido exitosamente",
        "user": current_user.to_dict()
    }), 200

@app.route("/api/perfil", methods=["PUT"])
@token_required
def actualizar_perfil(current_user):
    try:
        data = request.get_json()
        
        if 'nombre' in data and data['nombre'].strip():
            current_user.nombre_Usuario = data['nombre'].strip()
        
        if 'email' in data:
            nuevo_email = data['email'].strip().lower()
            if nuevo_email != current_user.email_Usuario:
                if Usuario.query.filter_by(email_Usuario=nuevo_email).first():
                    return jsonify({'message': 'El email ya está en uso'}), 400
                current_user.email_Usuario = nuevo_email
        
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'message': 'La contraseña debe tener al menos 6 caracteres'}), 400
            current_user.password_Usuario = generate_password_hash(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil actualizado exitosamente',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error interno', 'error': str(e)}), 500

# -------------------
# ENDPOINTS DE ADMINISTRACIÓN
# -------------------
@app.route("/api/admin/usuarios", methods=["GET"])
@token_required
@admin_required
def listar_usuarios(current_user):
    try:
        usuarios = Usuario.query.all()
        return jsonify({
            "message": "Usuarios obtenidos exitosamente",
            "usuarios": [usuario.to_dict() for usuario in usuarios]
        }), 200
    except Exception as e:
        return jsonify({"message": "Error interno", "error": str(e)}), 500

@app.route("/api/admin/usuarios/<int:user_id>", methods=["PUT"])
@token_required
@admin_required
def actualizar_usuario(current_user, user_id):
    try:
        usuario = Usuario.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'rol' in data:
            usuario.rol = data['rol']
        if 'is_active' in data:
            usuario.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            "message": "Usuario actualizado exitosamente",
            "user": usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error interno", "error": str(e)}), 500

@app.route("/api/admin/usuarios/<int:user_id>", methods=["DELETE"])
@token_required
@admin_required
def eliminar_usuario(current_user, user_id):
    try:
        if user_id == current_user.id_Usuario:
            return jsonify({"message": "No puedes eliminar tu propia cuenta"}), 400
            
        usuario = Usuario.query.get_or_404(user_id)
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({"message": "Usuario eliminado exitosamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error interno", "error": str(e)}), 500

# -------------------
# MANEJO DE ERRORES
# -------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Error interno del servidor'}), 500

# -------------------
# INICIALIZACIÓN
# -------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
        # Crear usuario admin por defecto si no existe
        admin = Usuario.query.filter_by(email_Usuario='admin@restaurant.com').first()
        if not admin:
            admin_user = Usuario(
                nombre_Usuario='Administrador',
                email_Usuario='admin@restaurant.com',
                password_Usuario=generate_password_hash('admin123'),
                rol=2  # Superadmin
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Usuario admin creado: admin@restaurant.com / admin123")
    
    print("🚀 Servidor iniciando en http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)