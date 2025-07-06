#!/bin/bash

# 🌐 Nginx Konfigürasyon Scripti
echo "🌐 Nginx konfigürasyonu ayarlanıyor..."

# Domain adını al
read -p "Domain adınızı girin (örn: kafka-basvuru.com): " DOMAIN

# Nginx config dosyası oluştur
sudo tee /etc/nginx/sites-available/kafka-basvuru > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Günlük dosyaları
    access_log /var/log/nginx/kafka-basvuru.access.log;
    error_log /var/log/nginx/kafka-basvuru.error.log;

    # Ana uygulama
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # Timeout ayarları
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static dosyalar
    location /static {
        alias /var/www/kafka-basvuru/web/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Upload dosyaları
    location /uploads {
        alias /var/www/kafka-basvuru/uploads;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Güvenlik başlıkları
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip sıkıştırma
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
}
EOF

# Symlink oluştur
sudo ln -sf /etc/nginx/sites-available/kafka-basvuru /etc/nginx/sites-enabled/

# Default site'ı kaldır
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx syntax kontrolü
if sudo nginx -t; then
    echo "✅ Nginx konfigürasyonu geçerli"
    sudo systemctl restart nginx
    echo "✅ Nginx yeniden başlatıldı"
else
    echo "❌ Nginx konfigürasyonu hatası!"
    exit 1
fi

echo "🌐 Nginx konfigürasyonu tamamlandı!"
echo "�� Domain: $DOMAIN" 