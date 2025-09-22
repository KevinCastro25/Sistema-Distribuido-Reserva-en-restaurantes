import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flask_cors import CORS
from functools import wraps

# ======================
# CONFIGURACIÓN APP
# ======================
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuración de base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "reservasRest.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "miclaveultrasecreta"

# Crear carpeta instance si no existe
os.makedirs(app.instance_path, exist_ok=True)

# ======================
# SQLALCHEMY
# ======================
db = SQLAlchemy(app)

# ======================
# MODELOS (Solo para gestión admin)
# ======================
class Usuario(db.Model):
    __tablename__ = "Usuario"
    id_Usuario = db.Column(db.Integer, primary_key=True)
    nombre_Usuario = db.Column(db.String(100), nullable=False)
    email_Usuario = db.Column(db.String(100), unique=True, nullable=False)
    password_Usuario = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.Integer, default=0)  # 0=cliente, 1=admin, 2=superadmin
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def check_password(self, password):
        return check_password_hash(self.password_Usuario, password)

    def generate_token(self):
        payload = {
            'id_Usuario': self.id_Usuario,
            'email': self.email_Usuario,
            'rol': self.rol,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
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

class Mesa(db.Model):
    __tablename__ = "Mesa"
    id_Mesa = db.Column(db.Integer, primary_key=True)
    numero_Mesa = db.Column(db.Integer, unique=True, nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    ubicacion = db.Column(db.String(50), nullable=True)
    estado_Mesa = db.Column(db.String(20), default="disponible")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id_Mesa,
            'numero': self.numero_Mesa,
            'capacidad': self.capacidad,
            'ubicacion': self.ubicacion,
            'estado': self.estado_Mesa,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Reserva(db.Model):
    __tablename__ = "Reserva"
    id_Reserva = db.Column(db.Integer, primary_key=True)
    id_Usuario = db.Column(db.Integer, db.ForeignKey("Usuario.id_Usuario"), nullable=False)
    id_Mesa = db.Column(db.Integer, db.ForeignKey("Mesa.id_Mesa"), nullable=False)
    fecha_Reserva = db.Column(db.Date, nullable=False)
    hora_Reserva = db.Column(db.Time, nullable=False)
    num_Personas = db.Column(db.Integer, nullable=False)
    estado_Reserva = db.Column(db.String(20), default="pendiente")
    comentarios = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relaciones
    usuario = db.relationship('Usuario', backref=db.backref('reservas', lazy=True))
    mesa = db.relationship('Mesa', backref=db.backref('reservas', lazy=True))

    def to_dict(self):
        return {
            'id': self.id_Reserva,
            'usuario_id': self.id_Usuario,
            'usuario_nombre': self.usuario.nombre_Usuario if self.usuario else 'Usuario eliminado',
            'usuario_email': self.usuario.email_Usuario if self.usuario else 'N/A',
            'mesa_id': self.id_Mesa,
            'mesa_numero': self.mesa.numero_Mesa if self.mesa else 'Mesa eliminada',
            'mesa_capacidad': self.mesa.capacidad if self.mesa else 0,
            'fecha': self.fecha_Reserva.isoformat() if self.fecha_Reserva else None,
            'hora': self.hora_Reserva.strftime('%H:%M') if self.hora_Reserva else None,
            'num_personas': self.num_Personas,
            'estado': self.estado_Reserva,
            'comentarios': self.comentarios,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ======================
# DECORADORES DE AUTENTICACIÓN
# ======================
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

# ======================
# RUTAS WEB (Templates de admin)
# ======================
@app.route("/")
def index():
    return render_template('login.html')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route("/admin")
def admin_panel():
    return render_template('admin/usuarios.html')

@app.route("/admin/mesas")
def admin_mesas():
    return render_template('admin/mesas.html')

@app.route("/admin/reservas")
def admin_reservas():
    return render_template('admin/reservas.html')
@app.route("/debug")
def debug_templates():
    import os
    template_path = os.path.join(app.root_path, 'templates', 'admin')
    files = os.listdir(template_path) if os.path.exists(template_path) else []
    return jsonify({
        "template_path": template_path,
        "files": files,
        "mesas_exists": os.path.exists(os.path.join(template_path, "mesas.html")),
        "reservas_exists": os.path.exists(os.path.join(template_path, "reservas.html"))
    })
# ======================
# ENDPOINTS API - AUTENTICACIÓN
# ======================
@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        nombre = data.get("nombre", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        rol = data.get("rol", 0)

        if not nombre or not email or not password:
            return jsonify({"message": "Todos los campos son requeridos"}), 400

        if len(password) < 6:
            return jsonify({"message": "La contraseña debe tener al menos 6 caracteres"}), 400

        if Usuario.query.filter_by(email_Usuario=email).first():
            return jsonify({"message": "El correo ya está registrado"}), 400

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

# ======================
# ENDPOINTS API - GESTIÓN DE USUARIOS
# ======================
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

# ======================
# ENDPOINTS API - GESTIÓN DE MESAS (Solo lectura y cambio de estado)
# ======================
@app.route("/api/admin/mesas", methods=["GET"])
@token_required
@admin_required
def listar_mesas(current_user):
    try:
        mesas = Mesa.query.all()
        return jsonify({
            "message": "Mesas obtenidas exitosamente",
            "mesas": [mesa.to_dict() for mesa in mesas]
        }), 200
    except Exception as e:
        return jsonify({"message": "Error interno", "error": str(e)}), 500

@app.route("/api/admin/mesas/<int:mesa_id>", methods=["PUT"])
@token_required
@admin_required
def actualizar_estado_mesa(current_user, mesa_id):
    try:
        mesa = Mesa.query.get_or_404(mesa_id)
        data = request.get_json()
        
        # Solo permitir cambio de estado para administración
        if 'estado' in data:
            estados_validos = ['disponible', 'ocupada', 'mantenimiento']
            if data['estado'] in estados_validos:
                mesa.estado_Mesa = data['estado']
            else:
                return jsonify({"message": "Estado no válido"}), 400
        
        db.session.commit()
        
        return jsonify({
            "message": "Estado de mesa actualizado exitosamente",
            "mesa": mesa.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error interno", "error": str(e)}), 500

# ======================
# ENDPOINTS API - GESTIÓN DE RESERVAS (Solo lectura y cambio de estado)
# ======================
@app.route("/api/admin/reservas", methods=["GET"])
@token_required
@admin_required
def listar_reservas(current_user):
    try:
        reservas = Reserva.query.order_by(Reserva.fecha_Reserva.desc(), Reserva.hora_Reserva.desc()).all()
        return jsonify({
            "message": "Reservas obtenidas exitosamente",
            "reservas": [reserva.to_dict() for reserva in reservas]
        }), 200
    except Exception as e:
        return jsonify({"message": "Error interno", "error": str(e)}), 500

@app.route("/api/admin/reservas/<int:reserva_id>", methods=["PUT"])
@token_required
@admin_required
def actualizar_reserva(current_user, reserva_id):
    try:
        reserva = Reserva.query.get_or_404(reserva_id)
        data = request.get_json()
        
        # Solo permitir cambio de estado y comentarios
        if 'estado' in data:
            estados_validos = ['pendiente', 'confirmada', 'cancelada', 'completada']
            if data['estado'] in estados_validos:
                reserva.estado_Reserva = data['estado']
            else:
                return jsonify({"message": "Estado no válido"}), 400
        
        if 'comentarios' in data:
            reserva.comentarios = data['comentarios']
        
        reserva.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "Reserva actualizada exitosamente",
            "reserva": reserva.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error interno", "error": str(e)}), 500

# ======================
# ENDPOINTS API - ESTADÍSTICAS
# ======================
@app.route("/api/admin/estadisticas", methods=["GET"])
@token_required
@admin_required
def obtener_estadisticas(current_user):
    try:
        # Estadísticas de usuarios
        total_usuarios = Usuario.query.count()
        usuarios_activos = Usuario.query.filter_by(is_active=True).count()
        admins = Usuario.query.filter(Usuario.rol >= 1).count()
        
        # Estadísticas de mesas
        total_mesas = Mesa.query.count()
        mesas_disponibles = Mesa.query.filter_by(estado_Mesa='disponible').count()
        mesas_ocupadas = Mesa.query.filter_by(estado_Mesa='ocupada').count()
        mesas_mantenimiento = Mesa.query.filter_by(estado_Mesa='mantenimiento').count()
        
        # Estadísticas de reservas
        total_reservas = Reserva.query.count()
        reservas_pendientes = Reserva.query.filter_by(estado_Reserva='pendiente').count()
        reservas_confirmadas = Reserva.query.filter_by(estado_Reserva='confirmada').count()
        
        # Reservas de hoy
        hoy = datetime.date.today()
        reservas_hoy = Reserva.query.filter_by(fecha_Reserva=hoy).count()
        
        return jsonify({
            "message": "Estadísticas obtenidas exitosamente",
            "estadisticas": {
                "usuarios": {
                    "total": total_usuarios,
                    "activos": usuarios_activos,
                    "inactivos": total_usuarios - usuarios_activos,
                    "administradores": admins
                },
                "mesas": {
                    "total": total_mesas,
                    "disponibles": mesas_disponibles,
                    "ocupadas": mesas_ocupadas,
                    "mantenimiento": mesas_mantenimiento
                },
                "reservas": {
                    "total": total_reservas,
                    "pendientes": reservas_pendientes,
                    "confirmadas": reservas_confirmadas,
                    "hoy": reservas_hoy
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Error interno", "error": str(e)}), 500

# ======================
# MANEJO DE ERRORES
# ======================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Error interno del servidor'}), 500

# ======================
# INICIALIZACIÓN
# ======================
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
    
    print("📌 Sistema de administración iniciado")
    print("🔗 Paneles disponibles:")
    print("   Login: http://127.0.0.1:5000")
    print("   Usuarios: http://127.0.0.1:5000/admin")
    print("   Mesas: http://127.0.0.1:5000/admin/mesas")
    print("   Reservas: http://127.0.0.1:5000/admin/reservas")
    print("🚀 Servidor iniciando...")
    app.run(debug=True)