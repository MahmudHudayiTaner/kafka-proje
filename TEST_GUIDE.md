# Test Kullanım Rehberi

Bu rehber, Kafka Proje testlerinin nasıl kullanılacağını açıklar.

## 📁 Test Yapısı

```
tests/
├── __init__.py          # Test modülü
├── test_basvuru.py     # Başvuru modeli testleri
└── test_web.py         # Web uygulaması testleri
```

## 🚀 Test Çalıştırma

### 1. Tüm Testleri Çalıştırma

```bash
python run_tests.py
```

Bu komut:
- Tüm test dosyalarını bulur
- Testleri çalıştırır
- Sonuçları raporlar

### 2. Belirli Test Dosyasını Çalıştırma

```bash
# Başvuru testleri
python -m unittest tests.test_basvuru

# Web testleri
python -m unittest tests.test_web
```

### 3. Belirli Test Metodunu Çalıştırma

```bash
# Sadece başvuru oluşturma testi
python -m unittest tests.test_basvuru.TestBasvuru.test_basvuru_olustur

# Sadece ana sayfa testi
python -m unittest tests.test_web.TestWebApp.test_ana_sayfa
```

## 📋 Test Kategorileri

### 1. Başvuru Testleri (`test_basvuru.py`)

**Test Edilen Özellikler:**
- ✅ Başvuru oluşturma
- ✅ Başvuru listeleme
- ✅ Başvuru silme
- ✅ Veri doğrulama

**Test Metodları:**
- `test_basvuru_olustur()` - Yeni başvuru oluşturma
- `test_basvuru_listele()` - Başvuru listesi alma
- `test_basvuru_sil()` - Başvuru silme
- `test_basvuru_validation()` - Veri doğrulama

### 2. Web Uygulaması Testleri (`test_web.py`)

**Test Edilen Özellikler:**
- ✅ Ana sayfa erişimi
- ✅ Başvuru formu gönderme
- ✅ Admin giriş sistemi
- ✅ Admin dashboard
- ✅ Başvuru listesi

**Test Metodları:**
- `test_ana_sayfa()` - Ana sayfa yükleme
- `test_basvuru_formu_gonder()` - Form gönderme
- `test_admin_login()` - Admin giriş
- `test_admin_dashboard()` - Dashboard erişimi
- `test_basvuru_listesi()` - Başvuru listesi

## 🔧 Test Konfigürasyonu

### Test Veritabanı
- Testler ayrı bir test veritabanı kullanır
- Her test öncesi temiz veritabanı
- Test sonrası otomatik temizlik

### Test Ortamı
- Flask test client kullanılır
- Gerçek HTTP istekleri simüle edilir
- Session yönetimi otomatik

## 📊 Test Sonuçları

Test çalıştırıldığında şu bilgiler görüntülenir:

```
🧪 Kafka Proje - Test Çalıştırılıyor...
==================================================
📁 2 test dosyası bulundu:
   - test_basvuru.py
   - test_web.py

🚀 Testler başlatılıyor...
--------------------------------------------------
test_basvuru_olustur (tests.test_basvuru.TestBasvuru) ... ok
test_basvuru_listele (tests.test_basvuru.TestBasvuru) ... ok
test_basvuru_sil (tests.test_basvuru.TestBasvuru) ... ok
test_basvuru_validation (tests.test_basvuru.TestBasvuru) ... ok
test_ana_sayfa (tests.test_web.TestWebApp) ... ok
test_basvuru_formu_gonder (tests.test_web.TestWebApp) ... ok
test_admin_login (tests.test_web.TestWebApp) ... ok
test_admin_dashboard (tests.test_web.TestWebApp) ... ok
test_basvuru_listesi (tests.test_web.TestWebApp) ... ok

==================================================
📊 Test Sonuçları:
   ✅ Başarılı: 9
   ❌ Başarısız: 0
   ⚠️  Hata: 0
   📝 Toplam: 9

🎉 Tüm testler başarıyla geçti!
```

## 🛠️ Yeni Test Ekleme

### 1. Test Dosyası Oluşturma

```python
# tests/test_yeni_ozellik.py
import unittest
import sys
import os

# Proje kök dizinini Python path'ine ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.database import Database

class TestYeniOzellik(unittest.TestCase):
    """Yeni özellik testleri"""
    
    def setUp(self):
        """Her test öncesi çalışır"""
        self.db = Database()
        
    def tearDown(self):
        """Her test sonrası çalışır"""
        pass
    
    def test_yeni_ozellik(self):
        """Yeni özellik testi"""
        # Test kodları buraya
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
```

### 2. Test Metodları

**Test Metod Adlandırma:**
- `test_` ile başlamalı
- Açıklayıcı isim kullan
- Örnek: `test_basvuru_olustur()`

**Assertion Metodları:**
- `self.assertEqual(a, b)` - Eşitlik kontrolü
- `self.assertIsNotNone(obj)` - None olmama kontrolü
- `self.assertTrue(condition)` - True kontrolü
- `self.assertIn(item, container)` - İçerik kontrolü

## 🐛 Hata Ayıklama

### Test Hatası Durumunda

1. **Hata Mesajını Oku:**
   ```
   AssertionError: 'beklenen' != 'gerçek'
   ```

2. **Test Verilerini Kontrol Et:**
   - Test verilerinin doğru olduğundan emin ol
   - Veritabanı durumunu kontrol et

3. **Debug Modunda Çalıştır:**
   ```bash
   python -m unittest tests.test_basvuru -v
   ```

### Yaygın Hatalar

1. **Import Hatası:**
   - Python path'inin doğru olduğundan emin ol
   - Modül adlarını kontrol et

2. **Veritabanı Hatası:**
   - Test veritabanının oluşturulduğunu kontrol et
   - Tablo yapısının doğru olduğunu kontrol et

3. **Web Test Hatası:**
   - Flask app'in doğru konfigüre edildiğini kontrol et
   - Test client'ın doğru çalıştığını kontrol et

## 📈 Test Geliştirme

### Best Practices

1. **Test İzolasyonu:**
   - Her test bağımsız olmalı
   - Test verilerini temizle

2. **Açıklayıcı İsimler:**
   - Test metodları açıklayıcı olmalı
   - Test verileri anlamlı olmalı

3. **Kapsamlı Test:**
   - Başarılı durumları test et
   - Hata durumlarını test et
   - Sınır değerleri test et

4. **Hızlı Test:**
   - Testler hızlı çalışmalı
   - Gereksiz işlemlerden kaçın

### Test Ekleme Önerileri

1. **Yeni Özellik Testleri:**
   - Her yeni özellik için test ekle
   - Hem başarılı hem hata durumlarını test et

2. **Entegrasyon Testleri:**
   - Bileşenler arası etkileşimi test et
   - End-to-end senaryoları test et

3. **Performans Testleri:**
   - Büyük veri setleri ile test et
   - Zaman aşımı durumlarını test et

## 🔍 Test Raporlama

### Otomatik Raporlama

Test çalıştırıldığında otomatik olarak:
- Başarılı test sayısı
- Başarısız test sayısı
- Hata sayısı
- Toplam test sayısı

### Manuel Raporlama

```bash
# Detaylı rapor
python run_tests.py > test_raporu.txt

# Sadece hataları
python run_tests.py 2>&1 | grep -E "(FAIL|ERROR)"
```

Bu rehber ile testlerinizi etkili bir şekilde kullanabilir ve projenizin kalitesini artırabilirsiniz. 