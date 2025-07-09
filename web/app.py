"""
Basit Başvuru Formu - Web Uygulaması
"""
import os
import sys
from flask import Flask

# src klasörünü Python path'ine ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from web.admin import admin_bp
from web.user import user_bp
from web.uploads import uploads_bp

app = Flask(__name__)
app.secret_key = 'kafka_proje_secret_key_2024'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 saat
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Blueprintleri kaydet
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)
app.register_blueprint(uploads_bp)

if __name__ == '__main__':
    import os
    from production_config import PRODUCTION_CONFIG
    if os.environ.get('FLASK_ENV') == 'production':
        app.config.update(PRODUCTION_CONFIG)
        app.run(
            host=PRODUCTION_CONFIG['HOST'],
            port=int(os.environ.get('PORT', PRODUCTION_CONFIG['PORT'])),
            debug=False
        )
    else:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        ) 