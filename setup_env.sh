#!/bin/bash

# 🔧 Environment Variables Setup Script
echo "🔧 Environment Variables Ayarlanıyor..."
echo "=================================================="

# Root kontrolü
if [ "$EUID" -ne 0 ]; then
    echo "❌ Bu script root yetkisi gerektirir!"
    echo "   sudo bash setup_env.sh"
    exit 1
fi

# Mevcut service dosyasını yedekle
cp /etc/systemd/system/kafka-basvuru.service /etc/systemd/system/kafka-basvuru.service.backup

# Environment variables'ları güncelle
echo "📝 Environment variables güncelleniyor..."

# Yeni service dosyası oluştur
cat > /etc/systemd/system/kafka-basvuru.service << EOF
[Unit]
Description=Kafka Dil Akademisi Web Uygulaması
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/kafka-basvuru
Environment=PATH=/var/www/kafka-basvuru/venv/bin
Environment=FLASK_ENV=production
Environment=FLASK_DEBUG=False
Environment=GEMINI_API_KEY=AIzaSyD2LkNVz4pus6dBjAF0aPQFcoUX3sR0OUo
Environment=SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
ExecStart=/var/www/kafka-basvuru/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 web.app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Systemd'yi yeniden yükle
systemctl daemon-reload

# Service'i yeniden başlat
echo "🔄 Service yeniden başlatılıyor..."
systemctl restart kafka-basvuru

# Durumu kontrol et
sleep 3
if systemctl is-active --quiet kafka-basvuru; then
    echo "✅ Environment variables başarıyla ayarlandı!"
    echo "✅ Uygulama çalışıyor!"
else
    echo "❌ Uygulama başlatılamadı!"
    systemctl status kafka-basvuru
    echo "📋 Logları kontrol edin:"
    echo "   sudo journalctl -u kafka-basvuru -n 50"
fi

echo "=================================================="
echo "🎉 Environment variables ayarlama tamamlandı!"
echo ""
echo "📝 Ayarlanan Environment Variables:"
echo "   FLASK_ENV=production"
echo "   FLASK_DEBUG=False"
echo "   GEMINI_API_KEY=AIzaSyD2LkNVz4pus6dBjAF0aPQFcoUX3sR0OUo"
echo "   SECRET_KEY=<random_generated>"
echo ""
echo "🔄 Service'i yeniden başlatmak için:"
echo "   sudo systemctl restart kafka-basvuru"
echo "==================================================" 