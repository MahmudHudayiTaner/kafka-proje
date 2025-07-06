#!/bin/bash

# 🚀 Kafka Proje - Lightsail Kurulum Scripti
echo "🚀 Kafka Proje - Lightsail Kurulumu Başlatılıyor..."
echo "=================================================="

# Sistem güncellemesi
echo "📦 Sistem güncelleniyor..."
sudo apt update && sudo apt upgrade -y

# Gerekli paketleri kur
echo "📦 Gerekli paketler kuruluyor..."
sudo apt install -y python3 python3-pip python3-venv nginx git curl wget unzip

# Python3-venv kurulumu
sudo apt install -y python3-venv

# Nginx'i başlat
echo "🌐 Nginx başlatılıyor..."
sudo systemctl start nginx
sudo systemctl enable nginx

# Firewall ayarları
echo "🔒 Firewall ayarları..."
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Proje dizini oluştur
echo "📁 Proje dizini oluşturuluyor..."
sudo mkdir -p /var/www/kafka-basvuru
sudo chown $USER:$USER /var/www/kafka-basvuru

# Git ile projeyi klonla (GitHub repository URL'nizi buraya ekleyin)
echo "📥 Proje indiriliyor..."
cd /var/www/kafka-basvuru
# git clone https://github.com/your-username/kafka-proje.git .

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
cat > .env << EOF
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
FLASK_ENV=production
EOF

# Gerekli dizinleri oluştur
echo "📁 Dizinler oluşturuluyor..."
mkdir -p data logs uploads web/uploads

# İzinleri ayarla
echo "🔐 İzinler ayarlanıyor..."
sudo chown -R www-data:www-data /var/www/kafka-basvuru
sudo chmod -R 755 /var/www/kafka-basvuru

echo "✅ Kurulum tamamlandı!"
echo "=================================================="
echo "🎯 Sonraki adımlar:"
echo "1. Nginx konfigürasyonu"
echo "2. SSL sertifikası"
echo "3. Systemd service"
echo "==================================================" 