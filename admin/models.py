# Modelos para la base de datos

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
	__tablename__ = "Usuario"
	id_Usuario = db.Column(db.Integer, primary_key=True)
	nombre_Usuario = db.Column(db.String(100), nullable=False)
	email_Usuario = db.Column(db.String(100), unique=True, nullable=False)
	password_Usuario = db.Column(db.String(200), nullable=False)
	rol = db.Column(db.Integer, default=0)

class Mesa(db.Model):
	__tablename__ = "Mesa"
	id_Mesa = db.Column(db.Integer, primary_key=True)
	capacidad = db.Column(db.Integer, nullable=False)
	estado_Mesa = db.Column(db.String(20), default="disponible")

class Reserva(db.Model):
	__tablename__ = "Reserva"
	id_Reserva = db.Column(db.Integer, primary_key=True)
	id_Usuario = db.Column(db.Integer, db.ForeignKey("Usuario.id_Usuario"), nullable=False)
	id_Mesa = db.Column(db.Integer, db.ForeignKey("Mesa.id_Mesa"), nullable=False)
	fecha_Reserva = db.Column(db.Date, nullable=False)
	hora_Reserva = db.Column(db.Time, nullable=False)
	num_Personas = db.Column(db.Integer, nullable=False)
	estado_Reserva = db.Column(db.String(20), default="pendiente")
