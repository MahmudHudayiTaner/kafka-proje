"""
Production konfigürasyon ayarları
"""
import os

PRODUCTION_CONFIG = {
    'HOST': '0.0.0.0',
    'PORT': 8000,
    'DEBUG': False,
    'TESTING': False,
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'kafka_proje_secret_key_2024_production'),
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
    'UPLOAD_FOLDER': 'uploads',
    'DATABASE_PATH': 'data/basvurular.db',
    'LOG_LEVEL': 'INFO',
    'LOG_PATH': 'logs/app.log'
} 