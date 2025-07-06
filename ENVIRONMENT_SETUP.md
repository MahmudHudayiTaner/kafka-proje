# 🔧 Environment Variables Ayarlama Rehberi

## 📋 **Sunucuda Environment Variables Ayarlama**

### 🚀 **Yöntem 1: Otomatik Script (Önerilen)**

```bash
# Script'i çalıştır
sudo bash setup_env.sh
```

### 🔧 **Yöntem 2: Manuel Ayarlama**

#### 1. **Systemd Service Dosyasını Düzenle**

```bash
sudo nano /etc/systemd/system/kafka-basvuru.service
```

#### 2. **Environment Variables Ekleyin**

```ini
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
Environment=SECRET_KEY=your_secret_key_here
ExecStart=/var/www/kafka-basvuru/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 web.app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. **Systemd'yi Yeniden Yükle**

```bash
sudo systemctl daemon-reload
sudo systemctl restart kafka-basvuru
```

### 🔧 **Yöntem 3: .env Dosyası (Alternatif)**

#### 1. **.env Dosyası Oluştur**

```bash
cd /var/www/kafka-basvuru
sudo nano .env
```

#### 2. **Environment Variables Ekle**

```env
FLASK_ENV=production
FLASK_DEBUG=False
GEMINI_API_KEY=AIzaSyD2LkNVz4pus6dBjAF0aPQFcoUX3sR0OUo
SECRET_KEY=your_secret_key_here
```

#### 3. **İzinleri Ayarla**

```bash
sudo chown www-data:www-data .env
sudo chmod 600 .env
```

### 🔧 **Yöntem 4: Export Komutları**

```bash
# Geçici olarak (terminal kapanınca kaybolur)
export FLASK_ENV=production
export FLASK_DEBUG=False
export GEMINI_API_KEY=AIzaSyD2LkNVz4pus6dBjAF0aPQFcoUX3sR0OUo
export SECRET_KEY=your_secret_key_here

# Service'i yeniden başlat
sudo systemctl restart kafka-basvuru
```

## 📋 **Environment Variables Listesi**

| Variable | Açıklama | Varsayılan Değer |
|----------|----------|-------------------|
| `FLASK_ENV` | Flask environment | `production` |
| `FLASK_DEBUG` | Debug modu | `False` |
| `GEMINI_API_KEY` | Gemini AI API Key | `AIzaSyD2LkNVz4pus6dBjAF0aPQFcoUX3sR0OUo` |
| `SECRET_KEY` | Flask secret key | `random_generated` |

## 🔍 **Kontrol Komutları**

### **Service Durumu Kontrol**

```bash
# Service durumu
sudo systemctl status kafka-basvuru

# Logları kontrol et
sudo journalctl -u kafka-basvuru -n 50

# Environment variables'ları kontrol et
sudo systemctl show kafka-basvuru --property=Environment
```

### **Environment Variables Test**

```bash
# Python ile test et
cd /var/www/kafka-basvuru
source venv/bin/activate
python -c "import os; print('FLASK_ENV:', os.environ.get('FLASK_ENV')); print('GEMINI_API_KEY:', os.environ.get('GEMINI_API_KEY')[:20] + '...')"
```

## 🚨 **Troubleshooting**

### **Service Başlatılamıyor**

```bash
# Logları kontrol et
sudo journalctl -u kafka-basvuru -n 100

# Manuel test
cd /var/www/kafka-basvuru
source venv/bin/activate
python run_web.py
```

### **Environment Variables Çalışmıyor**

```bash
# Service'i yeniden başlat
sudo systemctl daemon-reload
sudo systemctl restart kafka-basvuru

# Environment variables'ları kontrol et
sudo systemctl show kafka-basvuru --property=Environment
```

## 📝 **Notlar**

- ✅ **Systemd Service**: En güvenli ve kalıcı yöntem
- ✅ **Otomatik Script**: En kolay yöntem
- ⚠️ **Export**: Sadece geçici çözüm
- ⚠️ **.env Dosyası**: Flask uygulaması bunu otomatik okumaz

## 🎯 **Önerilen Yöntem**

1. **İlk Kurulum**: `sudo bash deploy.sh`
2. **Environment Variables**: `sudo bash setup_env.sh`
3. **Kontrol**: `sudo systemctl status kafka-basvuru` 