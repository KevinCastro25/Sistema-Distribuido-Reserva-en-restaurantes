from extensions import db
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask import current_app

class Usuario(db.Model):
    __tablename__ = "Usuario"
    id_Usuario = db.Column(db.Integer, primary_key=True)
    nombre_Usuario = db.Column(db.String(100), nullable=False)
    email_Usuario = db.Column(db.String(100), unique=True, nullable=False)
    password_Usuario = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, nombre_Usuario, email_Usuario, password_Usuario, rol=0):
        """Constructor del usuario"""
        self.nombre_Usuario = nombre_Usuario
        self.email_Usuario = email_Usuario
        self.password_Usuario = generate_password_hash(password_Usuario)
        self.rol = rol

    def check_password(self, password):
        """Verifica si la contraseña es correcta"""
        return check_password_hash(self.password_Usuario, password)

    def generate_token(self, expires_in=3600):
        """Genera un token JWT para el usuario"""
        payload = {
            'id_Usuario': self.id_Usuario,
            'email': self.email_Usuario,
            'rol': self.rol,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_token(token):
        """Verifica un token JWT y devuelve el usuario"""
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return Usuario.query.get(payload['id_Usuario'])
        except jwt.ExpiredSignatureError:
            return None  # Token expirado
        except jwt.InvalidTokenError:
            return None  # Token inválido


    def to_dict(self):
        """Convierte el usuario a diccionario (para JSON)"""
        return {
            'id': self.id_Usuario,
            'nombre': self.nombre_Usuario,
            'email': self.email_Usuario,
            'rol': self.rol,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.rol >= 1

    def is_superadmin(self):
        """Verifica si el usuario es superadministrador"""
        return self.rol >= 2

    def __repr__(self):
        return f'<Usuario {self.email_Usuario}>'

# -------------------
# MODELO CLIENTE (simplificado sin contraseñas)
# -------------------
class Cliente(db.Model):
    __tablename__ = "Cliente"
    id_Cliente = db.Column(db.Integer, primary_key=True)
    nombre_Cliente = db.Column(db.String(100), nullable=False)
    email_Cliente = db.Column(db.String(100), nullable=False)
    telefono_Cliente = db.Column(db.String(20), nullable=False)

# -------------------
# MODELO MESA
# -------------------
class Mesa(db.Model):
    __tablename__ = "Mesa"
    id_Mesa = db.Column(db.Integer, primary_key=True)
    numero_Mesa = db.Column(db.Integer, unique=True, nullable=False)
    capacidad_Mesa = db.Column(db.Integer, nullable=False)
    estado_Mesa = db.Column(db.String(20), default="disponible")  # disponible, ocupada, reservada

# -------------------
# MODELO RESERVA
# -------------------
class Reserva(db.Model):
    __tablename__ = "Reserva"
    id_Reserva = db.Column(db.Integer, primary_key=True)
    id_Cliente = db.Column(db.Integer, db.ForeignKey('Cliente.id_Cliente'), nullable=False)
    id_Mesa = db.Column(db.Integer, db.ForeignKey('Mesa.id_Mesa'), nullable=False)
    fecha_Reserva = db.Column(db.Date, nullable=False)
    hora_Reserva = db.Column(db.Time, nullable=False)
    num_Personas = db.Column(db.Integer, nullable=False)
    estado_Reserva = db.Column(db.String(20), default="pendiente")  # pendiente, confirmada, cancelada
    
    # Relaciones
    cliente = db.relationship('Cliente', backref=db.backref('reservas', lazy=True))
    mesa = db.relationship('Mesa', backref=db.backref('reservas', lazy=True))