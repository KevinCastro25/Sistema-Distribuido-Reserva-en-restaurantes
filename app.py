from flask import Flask
from flask_cors import CORS
from datetime import timedelta
from extensions import db, jwt
from models import Mesa
from clientes import clientes_bp
from reservas import reservas_bp
#from admin import admin_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///reservasRest.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "supersecretkey"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)

    # Blueprints
    app.register_blueprint(clientes_bp, url_prefix="/clientes")
    app.register_blueprint(reservas_bp, url_prefix="/reservas")
    #app.register_blueprint(admin_bp, url_prefix="/admin")


    def crear_datos_iniciales():
        # Crear mesas si no existen
        if not Mesa.query.first():
            mesas = [
                Mesa(numero_Mesa=1, capacidad_Mesa=4),
                Mesa(numero_Mesa=2, capacidad_Mesa=2),
                Mesa(numero_Mesa=3, capacidad_Mesa=6),
                Mesa(numero_Mesa=4, capacidad_Mesa=4),
                Mesa(numero_Mesa=5, capacidad_Mesa=8),
                Mesa(numero_Mesa=6, capacidad_Mesa=2),
                Mesa(numero_Mesa=7, capacidad_Mesa=4),
                Mesa(numero_Mesa=8, capacidad_Mesa=6)
            ]
            db.session.add_all(mesas)
            db.session.commit()
            print("Mesas creadas exitosamente")
    with app.app_context():
        db.create_all()
        crear_datos_iniciales()
    return app