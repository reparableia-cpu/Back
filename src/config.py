"""
Configuración centralizada de la aplicación
"""
import os
from decouple import config
from datetime import timedelta

class Config:
    """Configuración base"""
    SECRET_KEY = config('SECRET_KEY', default='asdf#FGSgvasgf$5$WGT')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = config(
        'DATABASE_URL', 
        default=f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    )
    
    # OpenAI
    OPENAI_API_KEY = config('OPENAI_API_KEY', default=None)
    
    # Redis (opcional)
    REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')
    
    # JWT
    JWT_SECRET_KEY = config('JWT_SECRET_KEY', default=SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS
    CORS_ORIGINS = config('CORS_ORIGINS', default='*', cast=lambda v: v.split(','))
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = config('UPLOAD_FOLDER', default='uploads')
    
    # Rate Limiting
    RATELIMIT_ENABLED = config('RATELIMIT_ENABLED', default=True, cast=bool)
    RATELIMIT_DEFAULT = config('RATELIMIT_DEFAULT', default='100/hour')

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Selección de configuración basada en entorno
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config():
    """Obtiene la configuración según el entorno"""
    env = config('FLASK_ENV', default='development')
    return config_dict.get(env, DevelopmentConfig)
