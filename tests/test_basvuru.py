import unittest
import sys
import os
import tempfile
import shutil
from datetime import datetime

# Proje kök dizinini Python path'ine ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.database import Database
from src.utils.validators import validate_basvuru_data


class TestBasvuru(unittest.TestCase):
    """Başvuru işlemleri testleri"""
    
    def setUp(self):
        """Her test öncesi çalışır"""
        # Test veritabanı için geçici dosya
        self.test_db_path = tempfile.mktemp(suffix='.db')
        
        # Test veritabanını başlat
        self.db = Database()
        self.db.db_path = self.test_db_path
        self.db._init_database()
        
    def tearDown(self):
        """Her test sonrası çalışır"""
        # Test veritabanını sil
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_basvuru_olustur(self):
        """Başvuru oluşturma testi"""
        print("Başvuru oluşturma testi ...", end=" ")
        
        # Test verisi
        basvuru_data = {
            'ad': 'Test Öğrenci',
            'soyad': 'Test',
            'telefon': '5551234567',
            'eposta': f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}@example.com',
            'dogum_tarihi': '2000-01-01',
            'cinsiyet': 'erkek',
            'adres': 'Test Adres',
            'kur_seviyesi': 'A1',
            'basvuru_tarihi': datetime.now()
        }
        
        # Başvuru ekle
        basvuru_id = self.db.basvuru_ekle(basvuru_data)
        
        # Kontrol et
        self.assertIsNotNone(basvuru_id)
        
        # Başvuruyu getir ve kontrol et
        basvuru = self.db.basvuru_getir(basvuru_id)
        self.assertIsNotNone(basvuru)
        self.assertEqual(basvuru['ad'], 'Test Öğrenci')
        self.assertEqual(basvuru['soyad'], 'Test')
        
        print("ok")
    
    def test_basvuru_listele(self):
        """Başvuru listeleme testi"""
        print("Başvuru listeleme testi ...", end=" ")
        
        # Test verileri ekle
        for i in range(2):
            basvuru_data = {
                'ad': f'Test Öğrenci {i+1}',
                'soyad': 'Test',
                'telefon': f'555123456{i}',
                'eposta': f'test{i}_{datetime.now().strftime("%Y%m%d_%H%M%S")}@example.com',
                'dogum_tarihi': '2000-01-01',
                'cinsiyet': 'erkek',
                'adres': 'Test Adres',
                'kur_seviyesi': 'A1',
                'basvuru_tarihi': datetime.now()
            }
            self.db.basvuru_ekle(basvuru_data)
        
        # Başvuruları listele
        basvurular = self.db.basvurulari_listele()
        
        # Kontrol et
        self.assertIsInstance(basvurular, list)
        self.assertGreaterEqual(len(basvurular), 2)
        
        print("ok")
    
    def test_basvuru_sil(self):
        """Başvuru silme testi"""
        print("Başvuru silme testi ...", end=" ")
        
        # Test verisi ekle
        basvuru_data = {
            'ad': 'Silinecek Öğrenci',
            'soyad': 'Test',
            'telefon': '5551234567',
            'eposta': f'sil_{datetime.now().strftime("%Y%m%d_%H%M%S")}@example.com',
            'dogum_tarihi': '2000-01-01',
            'cinsiyet': 'erkek',
            'adres': 'Test Adres',
            'kur_seviyesi': 'A1',
            'basvuru_tarihi': datetime.now()
        }
        
        basvuru_id = self.db.basvuru_ekle(basvuru_data)
        
        # Başvuruyu sil
        result = self.db.basvuru_sil(basvuru_id)
        
        # Kontrol et
        self.assertTrue(result)
        
        # Başvurunun silindiğini kontrol et
        basvuru = self.db.basvuru_getir(basvuru_id)
        self.assertIsNone(basvuru)
        
        print("ok")
    
    def test_basvuru_validation(self):
        """Başvuru doğrulama testi"""
        print("Başvuru doğrulama testi ...", end=" ")
        
        # Geçerli başvuru verisi
        valid_data = {
            'ad': 'Test Öğrenci',
            'soyad': 'Test',
            'telefon': '5551234567',
            'eposta': f'valid_{datetime.now().strftime("%Y%m%d_%H%M%S")}@example.com',
            'dogum_tarihi': '2000-01-01',
            'cinsiyet': 'erkek',
            'adres': 'Test Adres',
            'kur_seviyesi': 'A1',
            'basvuru_tarihi': datetime.now()
        }
        
        # Başvuru ekle
        basvuru_id = self.db.basvuru_ekle(valid_data)
        
        # Kontrol et
        self.assertIsNotNone(basvuru_id)
        
        # Aynı email ile tekrar başvuru yapmayı dene
        duplicate_data = valid_data.copy()
        duplicate_basvuru_id = self.db.basvuru_ekle(duplicate_data)
        
        # Kontrol et - aynı email ile başvuru yapılmamalı
        self.assertIsNone(duplicate_basvuru_id)
        
        print("ok")


if __name__ == '__main__':
    unittest.main() 