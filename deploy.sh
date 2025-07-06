#!/bin/bash

# 🚀 Kafka Proje - Ubuntu Deployment Script
echo "🚀 Kafka Proje - Ubuntu Deployment Başlatılıyor..."
echo "=================================================="

# Root kontrolü
if [ "$EUID" -ne 0 ]; then
    echo "❌ Bu script root yetkisi gerektirir!"
    echo "   sudo bash deploy.sh"
    exit 1
fi

# Sistem güncellemesi
echo "📦 Sistem güncelleniyor..."
apt update && apt upgrade -y

# Gerekli paketleri kur
echo "📦 Gerekli paketler kuruluyor..."
apt install -y python3 python3-pip python3-venv nginx git curl wget unzip ufw

# Nginx'i başlat
echo "🌐 Nginx başlatılıyor..."
systemctl start nginx
systemctl enable nginx

# Firewall ayarları
echo "🔒 Firewall ayarları..."
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Proje dizini oluştur
echo "📁 Proje dizini oluşturuluyor..."
mkdir -p /var/www/kafka-basvuru
chown $SUDO_USER:$SUDO_USER /var/www/kafka-basvuru

# Mevcut dosyaları kopyala
echo "📥 Proje dosyaları kopyalanıyor..."
cp -r ./* /var/www/kafka-basvuru/
cd /var/www/kafka-basvuru

# Virtual environment oluştur
echo "🐍 Python virtual environment oluşturuluyor..."
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları kur
echo "📦 Python bağımlılıkları kuruluyor..."
pip install --upgrade pip
pip install -r requirements.txt

# Environment variables oluştur
echo "🔧 Environment variables ayarlanıyor..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
cat > .env << EOF
SECRET_KEY=$SECRET_KEY
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
FLASK_ENV=production
EOF

# Gerekli dizinleri oluştur
echo "📁 Dizinler oluşturuluyor..."
mkdir -p data logs uploads web/uploads

# İzinleri ayarla
echo "🔐 İzinler ayarlanıyor..."
chown -R www-data:www-data /var/www/kafka-basvuru
chmod -R 755 /var/www/kafka-basvuru
chmod 600 .env

# Nginx konfigürasyonu
echo "🌐 Nginx konfigürasyonu..."
read -p "Domain adınızı girin (örn: kafka-basvuru.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    DOMAIN="localhost"
fi

# Nginx config oluştur
cat > /etc/nginx/sites-available/kafka-basvuru << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /var/www/kafka-basvuru/web/static;
    }
}
EOF

# Nginx symlink oluştur
ln -sf /etc/nginx/sites-available/kafka-basvuru /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Nginx syntax kontrolü
if nginx -t; then
    systemctl restart nginx
    echo "✅ Nginx konfigürasyonu tamamlandı"
else
    echo "❌ Nginx konfigürasyonu hatası!"
    exit 1
fi

# Systemd service oluştur
echo "🔧 Systemd service oluşturuluyor..."
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
ExecStart=/var/www/kafka-basvuru/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 web.app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Service'i etkinleştir
systemctl daemon-reload
systemctl enable kafka-basvuru
systemctl start kafka-basvuru

# Test et
echo "🧪 Uygulama test ediliyor..."
sleep 5

if systemctl is-active --quiet kafka-basvuru; then
    echo "✅ Uygulama başarıyla çalışıyor!"
else
    echo "❌ Uygulama başlatılamadı!"
    systemctl status kafka-basvuru
    exit 1
fi

echo "=================================================="
echo "🎉 Deployment tamamlandı!"
echo "🌐 Uygulama erişim bilgileri:"
echo "   URL: http://$DOMAIN"
echo "   Admin Panel: http://$DOMAIN/admin"
echo "   Admin Kullanıcı: admin"
echo "   Admin Şifre: admin123"
echo ""
echo "📝 Sonraki adımlar:"
echo "1. SSL sertifikası kurun: sudo certbot --nginx -d $DOMAIN"
echo "2. Admin şifresini değiştirin"
echo "3. Domain DNS ayarlarını yapın"
echo "==================================================" 