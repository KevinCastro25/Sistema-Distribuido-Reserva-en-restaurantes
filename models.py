from extensions import db

class Usuario(db.Model):
    id_Usuario = db.Column(db.Integer, primary_key=True)
    nombre_Usuario = db.Column(db.String(100), nullable=False)
    email_Usuario = db.Column(db.String(100), unique=True, nullable=False)
    password_Usuario = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.Integer, default=0)

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