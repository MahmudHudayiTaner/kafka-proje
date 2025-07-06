#!/bin/bash

# 🔧 Systemd Service Kurulum Scripti
echo "🔧 Systemd service kuruluyor..."

# Service dosyası oluştur
sudo tee /etc/systemd/system/kafka-basvuru.service > /dev/null << EOF
[Unit]
Description=Kafka Basvuru Web Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/kafka-basvuru
Environment=PATH=/var/www/kafka-basvuru/venv/bin
Environment=FLASK_ENV=production
ExecStart=/var/www/kafka-basvuru/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 web.app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

# Güvenlik ayarları
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/www/kafka-basvuru

[Install]
WantedBy=multi-user.target
EOF

# Service'i etkinleştir ve başlat
echo "🚀 Service etkinleştiriliyor..."
sudo systemctl daemon-reload
sudo systemctl enable kafka-basvuru
sudo systemctl start kafka-basvuru

# Durumu kontrol et
echo "📊 Service durumu kontrol ediliyor..."
sudo systemctl status kafka-basvuru --no-pager -l

# Logları göster
echo "📝 Son loglar:"
sudo journalctl -u kafka-basvuru -n 10 --no-pager

echo "✅ Systemd service kurulumu tamamlandı!"
echo "🔧 Yönetim komutları:"
echo "   Başlat: sudo systemctl start kafka-basvuru"
echo "   Durdur: sudo systemctl stop kafka-basvuru"
echo "   Yeniden başlat: sudo systemctl restart kafka-basvuru"
echo "   Durum: sudo systemctl status kafka-basvuru"
echo "   Loglar: sudo journalctl -u kafka-basvuru -f" 