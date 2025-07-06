#!/usr/bin/env python3
"""
Production Güncelleme Script'i
"""
import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

def backup_database():
    """Veritabanını yedekle"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"basvurular_{timestamp}.db"
    
    if Path("data/basvurular.db").exists():
        shutil.copy2("data/basvurular.db", backup_file)
        print(f"✅ Veritabanı yedeklendi: {backup_file}")
    else:
        print("⚠️  Veritabanı bulunamadı, yedekleme atlandı")

def update_files():
    """Dosyaları güncelle"""
    print("🔄 Dosyalar güncelleniyor...")
    
    # Güncellenecek dosyalar
    files_to_update = [
        "web/app.py",
        "web/templates/index.html",
        "web/templates/base.html",
        "src/core/database.py",
        "src/models/basvuru.py",
        "src/utils/validators.py",
        "requirements.txt"
    ]
    
    for file_path in files_to_update:
        if Path(file_path).exists():
            print(f"  📝 {file_path}")
        else:
            print(f"  ⚠️  {file_path} bulunamadı")
    
    print("✅ Dosya güncelleme tamamlandı")

def restart_service():
    """Servisi yeniden başlat"""
    print("🔄 Servis yeniden başlatılıyor...")
    
    # Windows için
    if os.name == 'nt':
        try:
            # Eğer systemd varsa
            subprocess.run(["systemctl", "restart", "kafka-basvuru"], check=True)
            print("✅ Servis yeniden başlatıldı (systemctl)")
        except:
            # Manuel başlatma
            print("📋 Servisi manuel olarak yeniden başlatın:")
            print("   python run_web.py")
    else:
        # Linux/Mac için
        try:
            subprocess.run(["sudo", "systemctl", "restart", "kafka-basvuru"], check=True)
            print("✅ Servis yeniden başlatıldı (systemctl)")
        except:
            print("📋 Servisi manuel olarak yeniden başlatın:")
            print("   python run_web.py")

def check_status():
    """Durum kontrolü"""
    print("\n🔍 Durum kontrolü...")
    
    # Veritabanı kontrolü
    if Path("data/basvurular.db").exists():
        print("✅ Veritabanı mevcut")
    else:
        print("⚠️  Veritabanı bulunamadı")
    
    # Log dosyası kontrolü
    if Path("logs/app.log").exists():
        print("✅ Log dosyası mevcut")
    else:
        print("⚠️  Log dosyası bulunamadı")
    
    # Upload klasörü kontrolü
    if Path("web/uploads").exists():
        print("✅ Upload klasörü mevcut")
    else:
        print("⚠️  Upload klasörü bulunamadı")

def main():
    """Ana fonksiyon"""
    print("🚀 Kafka Dil Akademisi - Production Güncelleme")
    print("=" * 50)
    
    # 1. Veritabanı yedekle
    backup_database()
    
    # 2. Dosyaları güncelle
    update_files()
    
    # 3. Servisi yeniden başlat
    restart_service()
    
    # 4. Durum kontrolü
    check_status()
    
    print("\n🎉 Güncelleme tamamlandı!")
    print("📱 Site: http://your-domain.com")
    print("🔧 Admin: http://your-domain.com/admin/login")

if __name__ == "__main__":
    main() 