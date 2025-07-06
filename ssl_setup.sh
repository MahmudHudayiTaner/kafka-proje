#!/bin/bash

# 🔒 SSL Sertifikası Kurulum Scripti
echo "🔒 SSL sertifikası kuruluyor..."

# Domain adını al
read -p "Domain adınızı girin (örn: kafka-basvuru.com): " DOMAIN

# Certbot kurulumu
echo "📦 Certbot kuruluyor..."
sudo apt install -y certbot python3-certbot-nginx

# SSL sertifikası al
echo "🔐 SSL sertifikası alınıyor..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Otomatik yenileme için cron job
echo "⏰ Otomatik yenileme ayarlanıyor..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# SSL durumunu kontrol et
echo "🔍 SSL durumu kontrol ediliyor..."
sudo certbot certificates

echo "✅ SSL sertifikası kurulumu tamamlandı!"
echo "🌐 https://$DOMAIN adresinden erişebilirsiniz" 