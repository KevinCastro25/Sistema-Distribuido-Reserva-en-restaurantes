from flask import Flask, render_template
from flask_cors import CORS
import os

# Importar configuraciones y modelos
from config import config
from models.usuario import db

# Importar blueprints
from routes.auth import auth_bp

def create_app(config_name=None):
    """Factory function para crear la aplicación Flask"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configurar CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    
    # Crear tablas de base de datos
    with app.app_context():
        db.create_all()
    
    # Rutas para servir templates (interfaz web)
    @app.route('/')
    def index():
        return render_template('login.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/admin')
    def admin():
        return render_template('admin/usuarios.html')
    
    # Manejar errores
    @app.errorhandler(404)
    def not_found(error):
        return {'message': 'Endpoint no encontrado'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'message': 'Error interno del servidor'}, 500
    
    return app

# Para desarrollo directo
if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='127.0.0.1', port=5000)