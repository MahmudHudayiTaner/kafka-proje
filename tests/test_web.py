import unittest
import sys
import os
import tempfile
import shutil
from datetime import datetime

# Proje kök dizinini Python path'ine ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from web.app import app
from src.core.database import Database


class TestWebApp(unittest.TestCase):
    """Web uygulaması testleri"""
    
    def setUp(self):
        """Her test öncesi çalışır"""
        # Test veritabanı için geçici dosya
        self.test_db_path = tempfile.mktemp(suffix='.db')
        
        # Test konfigürasyonu
        app.config['TESTING'] = True
        app.config['DATABASE_PATH'] = self.test_db_path
        
        # Test client oluştur
        self.client = app.test_client()
        
        # Test veritabanını başlat
        self.db = Database()
        self.db.db_path = self.test_db_path
        self.db._init_database()
        
    def tearDown(self):
        """Her test sonrası çalışır"""
        # Test veritabanını sil
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_ana_sayfa(self):
        """Ana sayfa testi"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Türkçe karakter kontrolü
        self.assertIn(b'Kafka Dil Akademisi', response.data)
    
    def test_basvuru_formu_gonder(self):
        """Başvuru formu gönderme testi"""
        test_data = {
            'ad': 'Test Öğrenci',
            'soyad': 'Test',
            'eposta': f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}@example.com',
            'telefon': '5551234567',
            'dogum_tarihi': '2000-01-01',
            'cinsiyet': 'erkek',
            'adres': 'Test Adres',
            'kur_seviyesi': 'A1'
        }
        
        # Form action'ı /submit olarak değiştir
        response = self.client.post('/submit', data=test_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Başarı mesajı kontrolü
        self.assertIn(b'ba\xc5\x9far\xc4\xb1yla', response.data)
    
    def test_admin_login(self):
        """Admin giriş testi"""
        # Geçersiz giriş
        response = self.client.post('/admin/login', data={
            'username': 'wrong',
            'password': 'wrong'
        }, follow_redirects=True)
        
        # Türkçe karakter kontrolü
        self.assertIn(b'Ge\xc3\xa7ersiz', response.data)
        
        # Geçerli giriş
        response = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        self.assertIn(b'Admin Dashboard', response.data)
    
    def test_admin_dashboard(self):
        """Admin dashboard testi"""
        # Giriş yapmadan erişim
        response = self.client.get('/admin/dashboard', follow_redirects=True)
        # Türkçe karakter kontrolü
        self.assertIn(b'Admin Giri\xc5\x9fi', response.data)
        
        # Giriş yap
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Dashboard'a erişim
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)
    
    def test_basvuru_listesi(self):
        """Başvuru listesi testi"""
        # Test verisi ekle
        test_data = {
            'ad': 'Test Öğrenci',
            'soyad': 'Test',
            'eposta': f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}@example.com',
            'telefon': '5551234567',
            'dogum_tarihi': '2000-01-01',
            'cinsiyet': 'erkek',
            'adres': 'Test Adres',
            'kur_seviyesi': 'A1',
            'basvuru_tarihi': '2025-07-05 23:00:00'
        }
        
        self.db.basvuru_ekle(test_data)
        
        # Giriş yap
        self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Başvuru listesine erişim
        response = self.client.get('/admin/basvurular')
        self.assertEqual(response.status_code, 200)
        # Türkçe karakter kontrolü
        self.assertIn(b'Ba\xc5\x9fvuru Listesi', response.data)


if __name__ == '__main__':
    unittest.main() 