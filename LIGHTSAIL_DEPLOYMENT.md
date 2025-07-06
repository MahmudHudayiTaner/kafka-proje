# 🚀 AWS Lightsail Deployment Rehberi

Bu rehber, Kafka Proje uygulamasını AWS Lightsail'de kurma adımlarını içerir.

## 📋 Ön Gereksinimler

- AWS Lightsail hesabı
- Domain adı (opsiyonel)
- SSH erişimi

## 🎯 Hızlı Kurulum

### **Adım 1: Lightsail Instance Oluştur**

1. **AWS Lightsail Console**'a giriş yapın
2. **Create instance** butonuna tıklayın
3. **Platform**: Linux/Unix
4. **Blueprint**: Ubuntu 22.04 LTS
5. **Instance plan**: $3.50/month (1GB RAM, 1 vCPU)
6. **Instance name**: kafka-basvuru
7. **Create instance** butonuna tıklayın

### **Adım 2: Static IP Atayın**

1. Instance oluşturulduktan sonra **Networking** sekmesine gidin
2. **Create static IP** butonuna tıklayın
3. **Static IP name**: kafka-basvuru-ip
4. **Create** butonuna tıklayın

### **Adım 3: SSH ile Bağlanın**

```bash
# Lightsail console'dan SSH butonuna tıklayın
# Veya terminal'den:
ssh -i ~/.ssh/LightsailDefaultKey-us-east-1.pem ubuntu@YOUR_INSTANCE_IP
```

## 🔧 Otomatik Kurulum

### **Adım 1: Scriptleri Yükleyin**

```bash
# Proje dosyalarını yükle
cd /home/ubuntu
wget https://raw.githubusercontent.com/your-username/kafka-proje/main/lightsail_setup.sh
wget https://raw.githubusercontent.com/your-username/kafka-proje/main/nginx_config.sh
wget https://raw.githubusercontent.com/your-username/kafka-proje/main/ssl_setup.sh
wget https://raw.githubusercontent.com/your-username/kafka-proje/main/service_setup.sh

# Scriptleri çalıştırılabilir yap
chmod +x *.sh
```

### **Adım 2: Temel Kurulum**

```bash
# Temel kurulumu çalıştır
./lightsail_setup.sh
```

### **Adım 3: Projeyi Yükleyin**

```bash
# Proje dizinine git
cd /var/www/kafka-basvuru

# Proje dosyalarını kopyala (local'den)
# scp -r /path/to/your/project/* ubuntu@YOUR_IP:/var/www/kafka-basvuru/

# Veya Git'ten klonla
git clone https://github.com/your-username/kafka-proje.git .

# Virtual environment'ı aktifleştir
source venv/bin/activate

# Bağımlılıkları kur
pip install -r requirements.txt
```

### **Adım 4: Nginx Konfigürasyonu**

```bash
# Nginx konfigürasyonu
./nginx_config.sh
```

### **Adım 5: SSL Sertifikası (Domain varsa)**

```bash
# SSL sertifikası kur
./ssl_setup.sh
```

### **Adım 6: Systemd Service**

```bash
# Service kurulumu
./service_setup.sh
```

## 🔧 Manuel Kurulum

### **Adım 1: Sistem Hazırlığı**

```bash
# Sistem güncellemesi
sudo apt update && sudo apt upgrade -y

# Gerekli paketler
sudo apt install -y python3 python3-pip python3-venv nginx git curl wget

# Nginx başlat
sudo systemctl start nginx
sudo systemctl enable nginx

# Firewall
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

### **Adım 2: Proje Kurulumu**

```bash
# Proje dizini
sudo mkdir -p /var/www/kafka-basvuru
sudo chown $USER:$USER /var/www/kafka-basvuru
cd /var/www/kafka-basvuru

# Proje dosyalarını kopyala
# (Local'den SCP ile veya Git'ten)

# Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Environment variables
cat > .env << EOF
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
FLASK_ENV=production
EOF

# Dizinler
mkdir -p data logs uploads web/uploads

# İzinler
sudo chown -R www-data:www-data /var/www/kafka-basvuru
sudo chmod -R 755 /var/www/kafka-basvuru
```

### **Adım 3: Nginx Konfigürasyonu**

```bash
# Nginx config
sudo tee /etc/nginx/sites-available/kafka-basvuru > /dev/null << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/kafka-basvuru/web/static;
    }

    location /uploads {
        alias /var/www/kafka-basvuru/uploads;
    }
}
EOF

# Symlink
sudo ln -sf /etc/nginx/sites-available/kafka-basvuru /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
```

### **Adım 4: Systemd Service**

```bash
# Service dosyası
sudo tee /etc/systemd/system/kafka-basvuru.service > /dev/null << 'EOF'
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
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Service'i etkinleştir
sudo systemctl daemon-reload
sudo systemctl enable kafka-basvuru
sudo systemctl start kafka-basvuru
```

## 🔒 SSL Sertifikası (Domain varsa)

```bash
# Certbot kur
sudo apt install -y certbot python3-certbot-nginx

# SSL sertifikası al
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Otomatik yenileme
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
```

## 📊 Monitoring ve Yönetim

### **Service Yönetimi**

```bash
# Durum kontrolü
sudo systemctl status kafka-basvuru

# Logları izle
sudo journalctl -u kafka-basvuru -f

# Yeniden başlat
sudo systemctl restart kafka-basvuru

# Nginx logları
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### **Veritabanı Yedekleme**

```bash
# Yedekle
sudo cp /var/www/kafka-basvuru/data/kafka_proje.db /home/ubuntu/backup_$(date +%Y%m%d_%H%M%S).db

# Otomatik yedekleme (cron)
(crontab -l 2>/dev/null; echo "0 2 * * * sudo cp /var/www/kafka-basvuru/data/kafka_proje.db /home/ubuntu/backup_$(date +\%Y\%m\%d).db") | crontab -
```

## 🌐 Domain Ayarları

### **DNS Ayarları**

1. Domain sağlayıcınızın DNS panelinde:
   - **A Record**: Lightsail IP adresinizi girin
   - **CNAME Record**: www → @

### **Cloudflare (Opsiyonel)**

1. [cloudflare.com](https://cloudflare.com) hesabı oluşturun
2. Domain'inizi ekleyin
3. DNS ayarlarını yapın
4. SSL sertifikasını etkinleştirin

## 🚨 Troubleshooting

### **Yaygın Sorunlar**

#### 1. **Service Başlamıyor**
```bash
# Detaylı log kontrolü
sudo journalctl -u kafka-basvuru -n 50

# Manuel test
cd /var/www/kafka-basvuru
source venv/bin/activate
gunicorn --bind 127.0.0.1:8000 web.app:app
```

#### 2. **Nginx Hatası**
```bash
# Syntax kontrolü
sudo nginx -t

# Konfigürasyon kontrolü
sudo nginx -T | grep server_name
```

#### 3. **Permission Denied**
```bash
# İzinleri düzelt
sudo chown -R www-data:www-data /var/www/kafka-basvuru
sudo chmod -R 755 /var/www/kafka-basvuru
```

#### 4. **Port Kullanımda**
```bash
# Port kontrolü
sudo netstat -tlnp | grep :8000

# Process'i bul ve durdur
sudo pkill -f gunicorn
```

## 📱 Test Etme

### **Kurulum Sonrası Kontroller**

1. ✅ **Ana sayfa**: http://YOUR_IP
2. ✅ **Admin paneli**: http://YOUR_IP/admin/login
3. ✅ **Başvuru formu**: http://YOUR_IP
4. ✅ **SSL** (domain varsa): https://your-domain.com
5. ✅ **Mobil uyumluluk**: Telefon/tablet'ten test

### **Admin Girişi**

- **Kullanıcı adı**: admin
- **Şifre**: admin123 (değiştirin!)

## 🔄 Güncelleme

### **Otomatik Güncelleme**

```bash
# Güncelleme scripti
cd /var/www/kafka-basvuru
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart kafka-basvuru
```

### **Manuel Güncelleme**

```bash
# Dosyaları güncelle (SCP ile)
# Servisi yeniden başlat
sudo systemctl restart kafka-basvuru
```

## 💰 Maliyet

- **Lightsail Instance**: $3.50/ay (1GB RAM, 1 vCPU)
- **Static IP**: Ücretsiz (ilk 5 adet)
- **Domain**: ~$10-15/yıl
- **SSL**: Ücretsiz (Let's Encrypt)

**Toplam**: ~$5-10/ay

## 🎉 Başarılı Deployment

Kurulum tamamlandığında:
- ✅ Uygulama çalışıyor
- ✅ Admin paneline erişim var
- ✅ SSL sertifikası aktif
- ✅ Domain ayarları tamam
- ✅ Monitoring aktif

Artık uygulamanız dış dünyadan erişilebilir! 🚀

---

**Not**: Güvenlik için admin şifresini değiştirmeyi unutmayın! 