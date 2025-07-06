#!/usr/bin/env python3
"""
Test çalıştırma scripti
"""
import sys
import os
import unittest
from pathlib import Path

def main():
    """Ana test fonksiyonu"""
    print("🧪 Kafka Proje - Test Çalıştırılıyor...")
    print("=" * 50)
    
    # Proje kök dizinini Python path'ine ekle
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Test klasörünü bul
    tests_dir = project_root / 'tests'
    
    if not tests_dir.exists():
        print("❌ tests klasörü bulunamadı!")
        return 1
    
    # Test dosyalarını bul
    test_files = []
    for test_file in tests_dir.glob('test_*.py'):
        test_files.append(str(test_file))
    
    if not test_files:
        print("❌ Test dosyası bulunamadı!")
        return 1
    
    print(f"📁 {len(test_files)} test dosyası bulundu:")
    for test_file in test_files:
        print(f"   - {os.path.basename(test_file)}")
    
    print("\n🚀 Testler başlatılıyor...")
    print("-" * 50)
    
    # Test loader oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Her test dosyasını yükle
    for test_file in test_files:
        try:
            # Test dosyasını modül olarak yükle
            module_name = os.path.splitext(os.path.basename(test_file))[0]
            test_module = __import__(f'tests.{module_name}', fromlist=['*'])
            
            # Test sınıflarını bul ve ekle
            for name in dir(test_module):
                obj = getattr(test_module, name)
                if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
                    tests = loader.loadTestsFromTestCase(obj)
                    suite.addTests(tests)
                    
        except Exception as e:
            print(f"❌ {test_file} yüklenirken hata: {e}")
    
    # Test runner oluştur
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True
    )
    
    # Testleri çalıştır
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print("📊 Test Sonuçları:")
    print(f"   ✅ Başarılı: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Başarısız: {len(result.failures)}")
    print(f"   ⚠️  Hata: {len(result.errors)}")
    print(f"   📝 Toplam: {result.testsRun}")
    
    if result.failures:
        print("\n❌ Başarısız Testler:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n⚠️  Hatalı Testler:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Başarı durumu
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 Tüm testler başarıyla geçti!")
    else:
        print("\n💥 Bazı testler başarısız oldu!")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main()) 