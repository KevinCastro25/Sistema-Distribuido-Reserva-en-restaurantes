from functools import wraps
from flask import request, jsonify, current_app
from models import Usuario
import jwt

def token_required(f):
    """Decorador para rutas que requieren autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]  # Formato: "Bearer <token>"
            except IndexError:
                return jsonify({'message': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'message': 'Token faltante'}), 401
        
        current_user = Usuario.verify_token(token)
        if not current_user:
            return jsonify({'message': 'Token inválido o expirado'}), 401
            
        if not current_user.is_active:
            return jsonify({'message': 'Usuario inactivo'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorador para rutas que requieren permisos de administrador"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'message': 'Permisos de administrador requeridos'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

def superadmin_required(f):
    """Decorador para rutas que requieren permisos de superadministrador"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_superadmin():
            return jsonify({'message': 'Permisos de superadministrador requeridos'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

def validate_user_data(data, required_fields):
    """Valida los datos del usuario"""
    errors = []
    
    for field in required_fields:
        if not data.get(field):
            errors.append(f'El campo {field} es requerido')
    
    email = data.get('email')
    if email and '@' not in email:
        errors.append('Formato de email inválido')
    
    password = data.get('password')
    if password and len(password) < 6:
        errors.append('La contraseña debe tener al menos 6 caracteres')
    
    return errors

def get_user_from_token():
    """Extrae el usuario actual del token en los headers"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        token = auth_header.split(" ")[1]
        return Usuario.verify_token(token)
    except:
        return None