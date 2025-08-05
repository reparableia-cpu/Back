"""
Funciones auxiliares y utilidades generales
"""
import json
import re
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import jsonify
from loguru import logger
import humanize
from slugify import slugify

def generate_uuid() -> str:
    """Generar UUID único"""
    return str(uuid.uuid4())

def generate_slug(text: str) -> str:
    """Generar slug URL-friendly"""
    return slugify(text, max_length=50)

def sanitize_filename(filename: str) -> str:
    """Sanitizar nombre de archivo"""
    # Remover caracteres no seguros
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limitar longitud
    name, ext = os.path.splitext(filename)
    if len(name) > 50:
        name = name[:50]
    return f"{name}{ext}"

def validate_email(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validar formato de teléfono básico"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None

def format_file_size(size_bytes: int) -> str:
    """Formatear tamaño de archivo en formato legible"""
    return humanize.naturalsize(size_bytes)

def format_datetime(dt: datetime, format_type: str = 'relative') -> str:
    """Formatear datetime en formato legible"""
    if format_type == 'relative':
        return humanize.naturaltime(dt)
    elif format_type == 'date':
        return dt.strftime('%Y-%m-%d')
    elif format_type == 'datetime':
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(dt)

def paginate_query(query, page: int = 1, per_page: int = 20):
    """Paginación de consultas SQLAlchemy"""
    return query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )

def success_response(data: Any = None, message: str = "Success", status_code: int = 200):
    """Respuesta JSON estándar para éxito"""
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code

def error_response(message: str = "Error", status_code: int = 400, details: Any = None):
    """Respuesta JSON estándar para errores"""
    response = {
        'success': False,
        'error': message
    }
    if details:
        response['details'] = details
    
    return jsonify(response), status_code

def log_request(request_data: Dict[str, Any], user_id: Optional[int] = None):
    """Loggear requests para debugging"""
    logger.info(f"Request from user {user_id}: {json.dumps(request_data, default=str)}")

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """JSON loads seguro que no falla"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extraer palabras clave básicas de un texto"""
    # Remover caracteres especiales y convertir a minúsculas
    clean_text = re.sub(r'[^\w\s]', '', text.lower())
    
    # Palabras comunes a ignorar (stop words básicas en español e inglés)
    stop_words = {
        'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'como', 'las', 'del', 'los', 'una', 'al', 'pero',
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from'
    }
    
    # Dividir en palabras y filtrar
    words = [word for word in clean_text.split() 
             if len(word) > 2 and word not in stop_words]
    
    # Contar frecuencias
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
    
    # Ordenar por frecuencia y retornar top keywords
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]

def create_directory_if_not_exists(path: str):
    """Crear directorio si no existe"""
    os.makedirs(path, exist_ok=True)

def is_valid_uuid(uuid_string: str) -> bool:
    """Validar si string es UUID válido"""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncar texto con sufijo"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
