"""
Yeni yapıyı test etmek için basit test dosyası
"""
import sys
import os

# src klasörünü Python path'ine ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.config import get_config
from core.logger import get_logger
from core.database import get_database
from models.basvuru import Basvuru, BasvuruDurumu
from utils.validators import validate_basvuru_data, sanitize_phone, sanitize_name
from datetime import datetime


def test_config():
    """Konfigürasyon testi"""
    print("🔧 Konfigürasyon testi...")
    try:
        config = get_config()
        print(f"✅ Konfigürasyon yüklendi: {config.get('mail')}")
        return True
    except Exception as e:
        print(f"❌ Konfigürasyon hatası: {e}")
        return False


def test_logger():
    """Logger testi"""
    print("📝 Logger testi...")
    try:
        logger = get_logger()
        logger.info("Test log mesajı")
        print("✅ Logger çalışıyor")
        return True
    except Exception as e:
        print(f"❌ Logger hatası: {e}")
        return False


def test_database():
    """Veritabanı testi"""
    print("🗄️ Veritabanı testi...")
    try:
        db = get_database()
        print("✅ Veritabanı bağlantısı başarılı")
        
        # İstatistikleri getir
        stats = db.istatistikler_getir()
        print(f"📊 Veritabanı istatistikleri: {stats}")
        return True
    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")
        return False


def test_basvuru_model():
    """Başvuru modeli testi"""
    print("📋 Başvuru modeli testi...")
    try:
        # Test verisi
        basvuru = Basvuru(
            ad="Ahmet",
            soyad="Yılmaz",
            telefon="+905551234567",
            eposta="ahmet@example.com",
            basvurulan_kur="Test Kurumu",
            basvuru_tarihi=datetime.now()
        )
        
        print(f"✅ Başvuru oluşturuldu: {basvuru}")
        
        # Sözlük formatına çevir
        basvuru_dict = basvuru.to_dict()
        print(f"📄 Sözlük formatı: {basvuru_dict}")
        
        # Sözlükten geri oluştur
        basvuru2 = Basvuru.from_dict(basvuru_dict)
        print(f"🔄 Sözlükten oluşturuldu: {basvuru2}")
        
        return True
    except Exception as e:
        print(f"❌ Başvuru modeli hatası: {e}")
        return False


def test_validators():
    """Doğrulama testi"""
    print("✅ Doğrulama testi...")
    try:
        # Test verisi
        test_data = {
            'ad': 'Ahmet',
            'soyad': 'Yılmaz',
            'telefon': '+905551234567',
            'eposta': 'ahmet@example.com',
            'basvurulan_kur': 'Test Kurumu',
            'basvuru_tarihi': '2024-01-15'
        }
        
        # Doğrulama
        is_valid, error = validate_basvuru_data(test_data)
        if is_valid:
            print("✅ Veri doğrulama başarılı")
        else:
            print(f"❌ Veri doğrulama hatası: {error}")
            return False
        
        # Temizleme testi
        phone = sanitize_phone("0555 123 45 67")
        name = sanitize_name("  ahmet   yılmaz  ")
        print(f"📱 Telefon temizlendi: {phone}")
        print(f"👤 İsim temizlendi: {name}")
        
        return True
    except Exception as e:
        print(f"❌ Doğrulama hatası: {e}")
        return False


def main():
    """Ana test fonksiyonu"""
    print("🚀 Yeni yapı testi başlıyor...\n")
    
    tests = [
        test_config,
        test_logger,
        test_database,
        test_basvuru_model,
        test_validators
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test hatası: {e}")
        print()
    
    print(f"📊 Test sonuçları: {passed}/{total} başarılı")
    
    if passed == total:
        print("🎉 Tüm testler başarılı! Yeni yapı hazır.")
    else:
        print("⚠️ Bazı testler başarısız. Lütfen hataları kontrol edin.")


if __name__ == "__main__":
    main() 