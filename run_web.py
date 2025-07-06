#!/usr/bin/env python3
"""
Web Uygulaması Başlatıcı
"""
import os
import sys
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Ana fonksiyon"""
    print("🚀 Kafka Proje - Web Uygulaması Başlatılıyor...")
    print("=" * 50)
    
    # Gerekli klasörleri oluştur
    folders = ['data', 'logs', 'web/uploads']
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"✅ {folder} klasörü hazır")
    
    # Web uygulamasını başlat
    try:
        from web.app import app
        
        # Debug modunu environment variable'dan al
        debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        
        print("\n🌐 Web uygulaması başlatılıyor...")
        print(f"🐛 Debug modu: {'Açık' if debug_mode else 'Kapalı'}")
        print("📱 Tarayıcıda http://localhost:5000 adresini açın")
        print("⏹️  Durdurmak için Ctrl+C tuşlayın")
        print("-" * 50)
        
        app.run(debug=debug_mode, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Web uygulaması durduruldu")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 