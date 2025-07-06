"""
Production Konfigürasyonu
"""
import os
from pathlib import Path
from datetime import timedelta

# Güvenlik ayarları
SECRET_KEY = os.environ.get('SECRET_KEY', 'kafka_proje_production_secret_key_2024')
DEBUG = False
TESTING = False

# Session ayarları
PERMANENT_SESSION_LIFETIME = timedelta(hours=2)  # 2 saat
SESSION_COOKIE_SECURE = True  # HTTPS için
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Dosya yükleme limitleri
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Veritabanı ayarları
DATABASE_URL = os.environ.get('DATABASE_URL', 'data/kafka_proje.db')

# Log ayarları
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/production.log'

# Admin ayarları
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Güvenlik başlıkları
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
}

# Production ayarları
PRODUCTION_CONFIG = {
    'DEBUG': False,
    'HOST': '0.0.0.0',
    'PORT': 5000,
    'SECRET_KEY': SECRET_KEY,
    'DATABASE_PATH': DATABASE_URL,
    'LOG_PATH': LOG_FILE,
    'UPLOAD_FOLDER': UPLOAD_FOLDER,
    'MAX_CONTENT_LENGTH': MAX_CONTENT_LENGTH,
    'ALLOWED_EXTENSIONS': ALLOWED_EXTENSIONS
}

# Development ayarları
DEVELOPMENT_CONFIG = {
    'DEBUG': True,
    'HOST': '127.0.0.1',
    'PORT': 5000,
    'SECRET_KEY': 'kafka_proje_secret_key_2024',
    'DATABASE_PATH': 'data/basvurular.db',
    'LOG_PATH': 'logs/app.log',
    'UPLOAD_FOLDER': 'web/uploads',
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
    'ALLOWED_EXTENSIONS': ['pdf']
}

def get_config():
    """Ortama göre konfigürasyon al"""
    if os.environ.get('FLASK_ENV') == 'production':
        return PRODUCTION_CONFIG
    else:
        return DEVELOPMENT_CONFIG 