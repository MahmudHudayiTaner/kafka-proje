# 🚀 Kafka Proje - Ubuntu Deployment Rehberi

Bu rehber, Kafka Proje uygulamasını Ubuntu server'a kurma adımlarını içerir.

## 📋 Ön Gereksinimler

- Ubuntu 18.04+ server
- Root erişimi
- Domain adı (opsiyonel)

## 🎯 Hızlı Deployment

### 1. GitHub'a Push

```bash
# Yerel projeyi GitHub'a push edin
git add .
git commit -m "Deployment için hazır"
git push origin main
```

### 2. Ubuntu Server'da Deployment

```bash
# Ubuntu server'a SSH ile bağlanın
ssh ubuntu@your-server-ip

# Projeyi GitHub'dan indirin
git clone https://github.com/your-username/kafka-proje.git
cd kafka-proje

# Deployment script'ini çalıştırın
sudo bash deploy.sh
```

## 🔧 Manuel Deployment

### Adım 1: Sistem Hazırlığı

```bash
# Sistem güncellemesi
sudo apt update && sudo apt upgrade -y

# Gerekli paketleri kur
sudo apt install -y python3 python3-pip python3-venv nginx git curl wget unzip ufw
```

### Adım 2: Proje Kurulumu

```bash
# Proje dizini oluştur
sudo mkdir -p /var/www/kafka-basvuru
sudo chown $USER:$USER /var/www/kafka-basvuru

# GitHub'dan projeyi indir
cd /var/www/kafka-basvuru
git clone https://github.com/your-username/kafka-proje.git .

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları kur
pip install --upgrade pip
pip install -r requirements.txt
```

### Adım 3: Environment Variables

```bash
# Secret key oluştur
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# .env dosyası oluştur
cat > .env << EOF
SECRET_KEY=$SECRET_KEY
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
FLASK_ENV=production
EOF

# İzinleri ayarla
sudo chown www-data:www-data .env
sudo chmod 600 .env
```

### Adım 4: Nginx Konfigürasyonu

```bash
# Domain adını girin
read -p "Domain adınızı girin: " DOMAIN

# Nginx config oluştur
sudo tee /etc/nginx/sites-available/kafka-basvuru > /dev/null << EOF
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

# Symlink oluştur
sudo ln -sf /etc/nginx/sites-available/kafka-basvuru /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx'i yeniden başlat
sudo nginx -t && sudo systemctl restart nginx
```

### Adım 5: Systemd Service

```bash
# Service dosyası oluştur
sudo tee /etc/systemd/system/kafka-basvuru.service > /dev/null << EOF
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
sudo systemctl daemon-reload
sudo systemctl enable kafka-basvuru
sudo systemctl start kafka-basvuru
```

### Adım 6: Firewall Ayarları

```bash
# Firewall ayarları
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## 🔒 SSL Sertifikası Kurulumu

```bash
# Certbot kur
sudo apt install -y certbot python3-certbot-nginx

# SSL sertifikası al
sudo certbot --nginx -d your-domain.com

# Otomatik yenileme
sudo crontab -e
# Şu satırı ekle:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring ve Logs

```bash
# Uygulama logları
sudo journalctl -u kafka-basvuru -f

# Nginx logları
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Service durumu
sudo systemctl status kafka-basvuru
```

## 🚨 Troubleshooting

### Yaygın Sorunlar

#### 1. Service Başlatılamıyor
```bash
# Logları kontrol et
sudo journalctl -u kafka-basvuru -n 50

# Manuel test et
cd /var/www/kafka-basvuru
source venv/bin/activate
gunicorn --bind 127.0.0.1:8000 web.app:app
```

#### 2. Nginx Hatası
```bash
# Nginx syntax kontrolü
sudo nginx -t

# Nginx logları
sudo tail -f /var/log/nginx/error.log
```

#### 3. Permission Denied
```bash
# İzinleri düzelt
sudo chown -R www-data:www-data /var/www/kafka-basvuru
sudo chmod -R 755 /var/www/kafka-basvuru
```

## 🔄 Güncelleme

```bash
# Projeyi güncelle
cd /var/www/kafka-basvuru
git pull origin main

# Bağımlılıkları güncelle
source venv/bin/activate
pip install -r requirements.txt

# Service'i yeniden başlat
sudo systemctl restart kafka-basvuru
```

## 🎉 Başarılı Deployment Sonrası

1. ✅ Uygulama çalışıyor
2. ✅ Admin paneline erişim var
3. ✅ Başvuru formu çalışıyor
4. ✅ SSL sertifikası aktif (opsiyonel)
5. ✅ Domain ayarları tamam

Artık uygulamanız dış dünyadan erişilebilir durumda! 🚀 