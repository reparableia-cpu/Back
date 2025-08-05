"""
Utilidades de autenticación y seguridad
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from typing import Dict, Any, Optional

def hash_password(password: str) -> str:
    """Hash de contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Verificar contraseña contra hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_token(user_id: int, token_type: str = 'access') -> str:
    """Generar JWT token"""
    now = datetime.utcnow()
    
    if token_type == 'access':
        expires = now + current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
    else:
        expires = now + current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
    
    payload = {
        'user_id': user_id,
        'type': token_type,
        'iat': now,
        'exp': expires
    }
    
    return jwt.encode(
        payload, 
        current_app.config['JWT_SECRET_KEY'], 
        algorithm='HS256'
    )

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodificar JWT token"""
    try:
        payload = jwt.decode(
            token, 
            current_app.config['JWT_SECRET_KEY'], 
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorador para rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Obtener token del header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Decodificar token
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Agregar user_id a request para uso en la función
        request.current_user_id = payload['user_id']
        
        return f(*args, **kwargs)
    
    return decorated_function

def generate_api_key() -> str:
    """Generar API key única"""
    import secrets
    return f"sk-{secrets.token_urlsafe(32)}"

def rate_limit_key(identifier: str) -> str:
    """Generar clave para rate limiting"""
    return f"rate_limit:{identifier}:{datetime.now().strftime('%Y-%m-%d-%H')}"
