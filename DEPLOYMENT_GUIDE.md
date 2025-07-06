# 🚀 Kafka Proje - Deployment Rehberi

Bu rehber, Kafka Proje uygulamasını sunucuya kurma ve dış erişim sağlama adımlarını içerir.

## 📋 Ön Gereksinimler

- Python 3.11+
- Git
- Sunucu hesabı (Railway, Render, Heroku vb.)

## 🎯 Hızlı Deployment Seçenekleri

### 1. **Railway (Önerilen - Ücretsiz)**

#### Adım 1: Railway Hesabı Oluştur
1. [railway.app](https://railway.app) adresine git
2. GitHub ile giriş yap
3. "New Project" → "Deploy from GitHub repo"

#### Adım 2: Projeyi Bağla
1. GitHub repository'nizi seçin
2. Railway otomatik olarak Python projesini algılayacak
3. "Deploy Now" butonuna tıklayın

#### Adım 3: Environment Variables Ayarla
Railway dashboard'da şu environment variables'ları ekleyin:
```
SECRET_KEY=your-super-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
```

#### Adım 4: Domain Ayarla
1. Railway dashboard'da "Settings" → "Domains"
2. Custom domain ekleyin veya Railway'in verdiği domain'i kullanın

### 2. **Render (Ücretsiz)**

#### Adım 1: Render Hesabı Oluştur
1. [render.com](https://render.com) adresine git
2. GitHub ile giriş yap
3. "New" → "Web Service"

#### Adım 2: Projeyi Bağla
1. GitHub repository'nizi seçin
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn web.app:app`

#### Adım 3: Environment Variables
Render dashboard'da environment variables ekleyin:
```
SECRET_KEY=your-super-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
```

### 3. **Heroku (Ücretli)**

#### Adım 1: Heroku CLI Kurulumu
```bash
# Windows için
# Heroku CLI'ı https://devcenter.heroku.com/articles/heroku-cli adresinden indirin

# macOS için
brew install heroku/brew/heroku
```

#### Adım 2: Heroku'ya Deploy
```bash
# Heroku'ya giriş
heroku login

# Yeni app oluştur
heroku create kafka-basvuru-app

# Environment variables ayarla
heroku config:set SECRET_KEY=your-super-secret-key-here
heroku config:set ADMIN_USERNAME=admin
heroku config:set ADMIN_PASSWORD=your-secure-password

# Deploy et
git push heroku main
```

## 🔧 Manuel Sunucu Kurulumu

### VPS/DigitalOcean Kurulumu

#### Adım 1: Sunucu Hazırlığı
```bash
# Ubuntu/Debian için
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# CentOS/RHEL için
sudo yum update
sudo yum install python3 python3-pip nginx
```

#### Adım 2: Projeyi İndir
```bash
# Git ile klonla
git clone https://github.com/your-username/kafka-proje.git
cd kafka-proje

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Bağımlılıkları kur
pip install -r requirements.txt
```

#### Adım 3: Gunicorn ile Çalıştır
```bash
# Gunicorn ile başlat
gunicorn --bind 0.0.0.0:8000 web.app:app --workers 4
```

#### Adım 4: Nginx Konfigürasyonu
```bash
# Nginx config dosyası oluştur
sudo nano /etc/nginx/sites-available/kafka-basvuru

# İçeriği:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/project/web/static;
    }
}

# Symlink oluştur
sudo ln -s /etc/nginx/sites-available/kafka-basvuru /etc/nginx/sites-enabled/

# Nginx'i yeniden başlat
sudo systemctl restart nginx
```

#### Adım 5: SSL Sertifikası (Let's Encrypt)
```bash
# Certbot kur
sudo apt install certbot python3-certbot-nginx

# SSL sertifikası al
sudo certbot --nginx -d your-domain.com

# Otomatik yenileme
sudo crontab -e
# Şu satırı ekle:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔒 Güvenlik Ayarları

### Environment Variables
```bash
# Güvenli secret key oluştur
python -c "import secrets; print(secrets.token_hex(32))"

# Environment variables ayarla
export SECRET_KEY="your-generated-secret-key"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="your-secure-password"
```

### Firewall Ayarları
```bash
# UFW firewall kur
sudo apt install ufw

# SSH ve HTTP/HTTPS portlarını aç
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Firewall'u etkinleştir
sudo ufw enable
```

## 📊 Monitoring ve Logs

### Systemd Service Oluştur
```bash
# Service dosyası oluştur
sudo nano /etc/systemd/system/kafka-basvuru.service

# İçeriği:
[Unit]
Description=Kafka Basvuru Web App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/kafka-basvuru
Environment="PATH=/var/www/kafka-basvuru/venv/bin"
ExecStart=/var/www/kafka-basvuru/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 web.app:app
Restart=always

[Install]
WantedBy=multi-user.target

# Service'i etkinleştir
sudo systemctl enable kafka-basvuru
sudo systemctl start kafka-basvuru
```

### Log Monitoring
```bash
# Logları izle
sudo journalctl -u kafka-basvuru -f

# Nginx logları
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🌐 Domain ve DNS Ayarları

### Domain Ayarları
1. Domain sağlayıcınızın DNS panelinde A record ekleyin
2. Sunucu IP adresinizi girin
3. CNAME record ile www subdomain'i yönlendirin

### Cloudflare (Opsiyonel)
1. [cloudflare.com](https://cloudflare.com) hesabı oluşturun
2. Domain'inizi ekleyin
3. DNS ayarlarını yapın
4. SSL sertifikasını etkinleştirin

## 🔄 Otomatik Deployment

### GitHub Actions ile CI/CD
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Railway
      uses: railway/deploy@v1
      with:
        railway_token: ${{ secrets.RAILWAY_TOKEN }}
```

## 📱 Mobil Uyumluluk

Uygulama zaten responsive tasarıma sahip. Bootstrap kullanıldığı için mobil cihazlarda da düzgün çalışır.

## 🚨 Troubleshooting

### Yaygın Sorunlar

#### 1. Port 5000 Kullanımda
```bash
# Farklı port kullan
gunicorn --bind 0.0.0.0:8000 web.app:app
```

#### 2. Permission Denied
```bash
# Dosya izinlerini düzelt
sudo chown -R www-data:www-data /var/www/kafka-basvuru
sudo chmod -R 755 /var/www/kafka-basvuru
```

#### 3. Database Bağlantı Hatası
```bash
# Veritabanı dosyasının izinlerini kontrol et
sudo chmod 666 /var/www/kafka-basvuru/data/kafka_proje.db
```

#### 4. Static Files Yüklenmiyor
```bash
# Nginx config'de static path'i kontrol et
location /static {
    alias /var/www/kafka-basvuru/web/static;
}
```

## 📞 Destek

Sorun yaşarsanız:
1. Logları kontrol edin
2. Environment variables'ları doğrulayın
3. Port ayarlarını kontrol edin
4. Firewall ayarlarını kontrol edin

## 🎉 Başarılı Deployment Sonrası

1. ✅ Uygulama çalışıyor
2. ✅ Admin paneline erişim var
3. ✅ Başvuru formu çalışıyor
4. ✅ SSL sertifikası aktif
5. ✅ Domain ayarları tamam

Artık uygulamanız dış dünyadan erişilebilir durumda! 🚀 