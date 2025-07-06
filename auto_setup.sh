#!/bin/bash

# Kafka Proje Otomatik Kurulum Scripti
# Bu script projeyi GitHub'dan çeker ve otomatik olarak kurar

set -e  # Hata durumunda dur

echo "🚀 Kafka Proje Otomatik Kurulum Başlıyor..."

# 1. Mevcut klasörü temizle
echo "📁 Mevcut klasör temizleniyor..."
cd /var/www
sudo rm -rf kafka-proje

# 2. GitHub'dan projeyi çek
echo "📥 GitHub'dan proje çekiliyor..."
sudo git clone https://github.com/MahmudHudayiTaner/kafka-proje.git
cd kafka-proje

# 3. Sahipliği değiştir
echo "👤 Klasör sahipliği değiştiriliyor..."
sudo chown -R ubuntu:ubuntu /var/www/kafka-proje

# 4. Python virtual environment oluştur
echo "🐍 Python virtual environment oluşturuluyor..."
python3 -m venv venv
source venv/bin/activate

# 5. Gerekli paketleri yükle
echo "📦 Gerekli paketler yükleniyor..."
pip install -r requirements.txt

# 6. Gerekli klasörleri oluştur ve izinleri ayarla
echo "📂 Gerekli klasörler oluşturuluyor..."
mkdir -p logs uploads data
sudo chown -R ubuntu:ubuntu /var/www/kafka-proje
sudo chmod -R 755 /var/www/kafka-proje
sudo chmod 644 /var/www/kafka-proje/logs/app.log 2>/dev/null || true

# 7. Systemd servis dosyasını oluştur
echo "⚙️ Systemd servis dosyası oluşturuluyor..."
sudo tee /etc/systemd/system/kafka-proje.service > /dev/null <<EOF
[Unit]
Description=Kafka Dil Akademisi Web Uygulaması
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/kafka-proje
Environment=PATH=/var/www/kafka-proje/venv/bin
ExecStart=/var/www/kafka-proje/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 web.app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 8. Servisi etkinleştir ve başlat
echo "🚀 Servis başlatılıyor..."
sudo systemctl daemon-reload
sudo systemctl enable kafka-proje
sudo systemctl start kafka-proje

# 9. Durumu kontrol et
echo "✅ Kurulum tamamlandı!"
echo "📊 Servis durumu:"
sudo systemctl status kafka-proje --no-pager

echo ""
echo "🎉 Kurulum başarıyla tamamlandı!"
echo "🌐 Uygulama http://localhost:8000 adresinde çalışıyor"
echo "📝 Logları görmek için: sudo journalctl -u kafka-proje -f" 