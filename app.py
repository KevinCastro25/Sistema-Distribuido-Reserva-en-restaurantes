from flask import Flask
from flask_cors import CORS
from datetime import timedelta
from extensions import db, jwt
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

    with app.app_context():
        db.create_all()

    return app
