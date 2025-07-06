#!/usr/bin/env python3
"""
Kafka Proje - Stabilite ve Güvenlik Testleri
Bu script projenin çeşitli hata senaryolarında nasıl davrandığını test eder.
"""

import sys
import os
import tempfile
import shutil
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
sys.path.insert(0, os.path.dirname(__file__))

from src.core.database import Database
from src.utils.validators import validate_basvuru_data, sanitize_name, sanitize_phone
from src.models.basvuru import Basvuru


class StabilityTester:
    """Proje stabilite testleri"""
    
    def __init__(self):
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.db = Database()
        self.db.db_path = self.test_db_path
        self.test_results = []
        
    def setup(self):
        """Test ortamını hazırla"""
        print("🔧 Test ortamı hazırlanıyor...")
        self.db._init_database()
        print("✅ Test ortamı hazır")
        
    def cleanup(self):
        """Test ortamını temizle"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        print("🧹 Test ortamı temizlendi")
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Test sonucunu kaydet"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
    
    def test_1_database_limits(self):
        """Test 1: Veritabanı sınırları"""
        print("\n📊 Test 1: Veritabanı Sınırları")
        
        try:
            # Çok uzun veriler ekle
            long_data = {
                'ad': 'A' * 1000,  # 1000 karakterlik isim
                'soyad': 'B' * 1000,
                'telefon': '1' * 50,
                'eposta': 'test@example.com',
                'dogum_tarihi': '2000-01-01',
                'cinsiyet': 'erkek',
                'adres': 'C' * 2000,  # 2000 karakterlik adres
                'kur_seviyesi': 'A1',
                'basvuru_tarihi': datetime.now()
            }
            
            basvuru_id = self.db.basvuru_ekle(long_data)
            self.log_test("Uzun veri ekleme", basvuru_id is not None, 
                         f"1000+ karakterlik veriler eklendi")
            
            # Çok sayıda kayıt ekle
            for i in range(1000):
                data = {
                    'ad': f'Test{i}',
                    'soyad': 'User',
                    'telefon': f'555123456{i%1000:03d}',
                    'eposta': f'test{i}@example.com',
                    'dogum_tarihi': '2000-01-01',
                    'cinsiyet': 'erkek',
                    'adres': f'Test Adres {i}',
                    'kur_seviyesi': 'A1',
                    'basvuru_tarihi': datetime.now()
                }
                self.db.basvuru_ekle(data)
            
            basvurular = self.db.basvurulari_listele(limit=1000)
            self.log_test("Çok sayıda kayıt", len(basvurular) >= 1000, 
                         f"{len(basvurular)} kayıt eklendi")
            
        except Exception as e:
            self.log_test("Veritabanı sınırları", False, f"Hata: {str(e)}")
    
    def test_2_malicious_input(self):
        """Test 2: Kötü niyetli girdiler"""
        print("\n🚨 Test 2: Kötü Niyetli Girdiler")
        
        malicious_inputs = [
            # SQL Injection denemeleri
            {'ad': "'; DROP TABLE basvurular; --", 'soyad': 'Test'},
            {'ad': "' OR '1'='1", 'soyad': 'Test'},
            {'ad': "'; INSERT INTO basvurular VALUES (999, 'hack', 'hack', '123', 'hack@hack.com', '2000-01-01', 'erkek', 'hack', 'A1', datetime.now(), NULL, NULL, NULL, 'beklemede', datetime.now()); --", 'soyad': 'Test'},
            
            # XSS denemeleri
            {'ad': '<script>alert("XSS")</script>', 'soyad': 'Test'},
            {'ad': '<img src="x" onerror="alert(1)">', 'soyad': 'Test'},
            
            # Boş ve null değerler
            {'ad': '', 'soyad': ''},
            {'ad': None, 'soyad': None},
            {'ad': '   ', 'soyad': '   '},
            
            # Özel karakterler
            {'ad': 'Test\x00User', 'soyad': 'Test'},
            {'ad': 'Test\nUser', 'soyad': 'Test'},
            {'ad': 'Test\rUser', 'soyad': 'Test'},
        ]
        
        for i, malicious_data in enumerate(malicious_inputs):
            try:
                # Temizleme işlemi
                cleaned_name = sanitize_name(malicious_data.get('ad', ''))
                cleaned_phone = sanitize_phone(malicious_data.get('telefon', ''))
                
                # Veri doğrulama
                test_data = {
                    'ad': cleaned_name,
                    'soyad': malicious_data.get('soyad', 'Test'),
                    'telefon': cleaned_phone or '5551234567',
                    'eposta': 'test@example.com',
                    'dogum_tarihi': '2000-01-01',
                    'cinsiyet': 'erkek',
                    'adres': 'Test Adres',
                    'kur_seviyesi': 'A1',
                    'basvuru_tarihi': datetime.now()
                }
                
                is_valid, error = validate_basvuru_data(test_data)
                
                if is_valid:
                    basvuru_id = self.db.basvuru_ekle(test_data)
                    self.log_test(f"Kötü girdi {i+1}", basvuru_id is not None, 
                                 f"Temizlendi ve kaydedildi: {cleaned_name[:20]}...")
                else:
                    self.log_test(f"Kötü girdi {i+1}", True, 
                                 f"Geçersiz veri reddedildi: {error}")
                    
            except Exception as e:
                self.log_test(f"Kötü girdi {i+1}", False, f"Hata: {str(e)}")
    
    def test_3_concurrent_access(self):
        """Test 3: Eşzamanlı erişim"""
        print("\n🔄 Test 3: Eşzamanlı Erişim")
        
        def worker(worker_id):
            """Çalışan thread fonksiyonu"""
            try:
                for i in range(10):
                    data = {
                        'ad': f'Worker{worker_id}_User{i}',
                        'soyad': 'Test',
                        'telefon': f'555123456{worker_id}{i:02d}',
                        'eposta': f'worker{worker_id}_test{i}@example.com',
                        'dogum_tarihi': '2000-01-01',
                        'cinsiyet': 'erkek',
                        'adres': f'Worker {worker_id} Adres {i}',
                        'kur_seviyesi': 'A1',
                        'basvuru_tarihi': datetime.now()
                    }
                    
                    basvuru_id = self.db.basvuru_ekle(data)
                    if basvuru_id:
                        print(f"  Worker {worker_id}: Kayıt {i+1} eklendi (ID: {basvuru_id})")
                    
                    time.sleep(0.01)  # Kısa bekleme
                    
            except Exception as e:
                print(f"  Worker {worker_id} hatası: {e}")
        
        # 5 thread ile eşzamanlı erişim
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Thread'lerin bitmesini bekle
        for thread in threads:
            thread.join()
        
        # Sonuçları kontrol et
        basvurular = self.db.basvurulari_listele(limit=1000)
        expected_count = 5 * 10  # 5 worker * 10 kayıt
        
        self.log_test("Eşzamanlı erişim", len(basvurular) >= expected_count,
                     f"{len(basvurular)} kayıt eklendi (beklenen: ~{expected_count})")
    
    def test_4_memory_usage(self):
        """Test 4: Bellek kullanımı"""
        print("\n💾 Test 4: Bellek Kullanımı")
        
        try:
            import psutil
            import gc
            
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Çok sayıda büyük veri ekle
            for i in range(100):
                large_data = {
                    'ad': f'LargeUser{i}',
                    'soyad': 'Test',
                    'telefon': f'555123456{i:02d}',
                    'eposta': f'large{i}@example.com',
                    'dogum_tarihi': '2000-01-01',
                    'cinsiyet': 'erkek',
                    'adres': 'X' * 1000,  # 1000 karakterlik adres
                    'kur_seviyesi': 'A1',
                    'basvuru_tarihi': datetime.now(),
                    'pdf_icerik': 'Y' * 50000,  # 50KB PDF içeriği
                    'ai_analiz_sonucu': 'Z' * 10000  # 10KB AI analiz
                }
                
                self.db.basvuru_ekle(large_data)
            
            # Bellek temizliği
            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            self.log_test("Bellek kullanımı", memory_increase < 100,  # 100MB'dan az artış
                         f"Bellek artışı: {memory_increase:.2f}MB")
            
        except ImportError:
            self.log_test("Bellek kullanımı", True, "psutil kütüphanesi yok, test atlandı")
        except Exception as e:
            self.log_test("Bellek kullanımı", False, f"Hata: {str(e)}")
    
    def test_5_data_integrity(self):
        """Test 5: Veri bütünlüğü"""
        print("\n🔒 Test 5: Veri Bütünlüğü")
        
        try:
            # Test verisi ekle
            test_data = {
                'ad': 'Integrity Test',
                'soyad': 'User',
                'telefon': '5551234567',
                'eposta': 'integrity@test.com',
                'dogum_tarihi': '2000-01-01',
                'cinsiyet': 'erkek',
                'adres': 'Test Adres',
                'kur_seviyesi': 'A1',
                'basvuru_tarihi': datetime.now()
            }
            
            basvuru_id = self.db.basvuru_ekle(test_data)
            
            # Veriyi getir ve kontrol et
            if basvuru_id is not None:
                retrieved_data = self.db.basvuru_getir(basvuru_id)
                
                # Veri bütünlüğü kontrolü
                if retrieved_data is not None:
                    integrity_ok = (
                        retrieved_data['ad'] == test_data['ad'] and
                        retrieved_data['soyad'] == test_data['soyad'] and
                        retrieved_data['telefon'] == test_data['telefon'] and
                        retrieved_data['eposta'] == test_data['eposta']
                    )
                else:
                    integrity_ok = False
            else:
                integrity_ok = False
            
            self.log_test("Veri bütünlüğü", integrity_ok, 
                         "Kaydedilen ve okunan veriler eşleşiyor")
            
            # Aynı email ile tekrar kayıt denemesi
            duplicate_data = test_data.copy()
            duplicate_id = self.db.basvuru_ekle(duplicate_data)
            
            self.log_test("Tekrar kayıt kontrolü", duplicate_id is None,
                         "Aynı email ile tekrar kayıt engellendi")
            
        except Exception as e:
            self.log_test("Veri bütünlüğü", False, f"Hata: {str(e)}")
    
    def test_6_error_handling(self):
        """Test 6: Hata yönetimi"""
        print("\n⚠️ Test 6: Hata Yönetimi")
        
        # Geçersiz veritabanı yolu
        try:
            invalid_db = Database()
            invalid_db.db_path = "/invalid/path/database.db"
            invalid_db._init_database()
            self.log_test("Geçersiz DB yolu", False, "Hata yakalanmalıydı")
        except Exception:
            self.log_test("Geçersiz DB yolu", True, "Hata düzgün yakalandı")
        
        # Geçersiz veri tipleri
        try:
            invalid_data = {
                'ad': 123,  # String olmalı
                'soyad': None,
                'telefon': [],
                'eposta': 456,
                'dogum_tarihi': 'invalid-date',
                'cinsiyet': 'invalid',
                'adres': '',
                'kur_seviyesi': '',
                'basvuru_tarihi': 'not-a-datetime'
            }
            
            basvuru_id = self.db.basvuru_ekle(invalid_data)
            self.log_test("Geçersiz veri tipleri", basvuru_id is None,
                         "Geçersiz veriler reddedildi")
            
        except Exception as e:
            self.log_test("Geçersiz veri tipleri", True, f"Hata yakalandı: {str(e)}")
    
    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print("🚀 Kafka Proje - Stabilite Testleri Başlatılıyor...")
        print("=" * 60)
        
        self.setup()
        
        try:
            self.test_1_database_limits()
            self.test_2_malicious_input()
            self.test_3_concurrent_access()
            self.test_4_memory_usage()
            self.test_5_data_integrity()
            self.test_6_error_handling()
            
        finally:
            self.cleanup()
        
        # Sonuçları özetle
        self.print_summary()
    
    def print_summary(self):
        """Test sonuçlarını özetle"""
        print("\n" + "=" * 60)
        print("📊 TEST SONUÇLARI ÖZETİ")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Toplam Test: {total_tests}")
        print(f"✅ Başarılı: {passed_tests}")
        print(f"❌ Başarısız: {failed_tests}")
        print(f"📈 Başarı Oranı: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ BAŞARISIZ TESTLER:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n💡 ÖNERİLER:")
        if failed_tests == 0:
            print("  ✅ Proje stabilite testlerini geçti!")
            print("  ✅ Güvenlik önlemleri yeterli")
            print("  ✅ Veritabanı sınırları uygun")
        else:
            print("  ⚠️ Bazı testler başarısız oldu")
            print("  🔧 Hataları düzeltmek için kodları gözden geçirin")
            print("  🛡️ Güvenlik önlemlerini artırın")


if __name__ == '__main__':
    tester = StabilityTester()
    tester.run_all_tests() 