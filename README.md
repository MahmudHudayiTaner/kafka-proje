# Kafka Dil Akademisi - Başvuru Sistemi

PDF dekont analizi yapan web uygulaması. Gemini AI ile otomatik dekont analizi.

## 🚀 Hızlı Kurulum

### Sunucuda Otomatik Kurulum

```bash
# 1. Scripti indirin
wget https://raw.githubusercontent.com/MahmudHudayiTaner/kafka-proje/main/auto_setup.sh

# 2. Çalıştırılabilir yapın
chmod +x auto_setup.sh

# 3. Otomatik kurulumu başlatın
sudo ./auto_setup.sh
```

### Manuel Kurulum

```bash
# 1. Projeyi klonlayın
git clone https://github.com/MahmudHudayiTaner/kafka-proje.git
cd kafka-proje

# 2. Virtual environment oluşturun
python3 -m venv venv
source venv/bin/activate

# 3. Gerekli paketleri yükleyin
pip install -r requirements.txt

# 4. Gerekli klasörleri oluşturun
mkdir -p logs uploads data

# 5. Uygulamayı başlatın
python run_web.py
```

## 🌐 Kullanım

- **Ana Sayfa**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin/login
  - Kullanıcı: `admin`
  - Şifre: `admin123`

## 📁 Proje Yapısı

```
kafka-proje/
├── src/                    # Ana kaynak kodlar
│   ├── core/              # Çekirdek modüller
│   ├── models/            # Veritabanı modelleri
│   ├── services/          # Servisler (PDF analiz)
│   └── utils/             # Yardımcı fonksiyonlar
├── web/                   # Web uygulaması
│   ├── app.py            # Flask uygulaması
│   ├── static/           # CSS, JS dosyaları
│   └── templates/        # HTML şablonları
├── auto_setup.sh         # Otomatik kurulum scripti
├── run_web.py            # Geliştirme sunucusu
└── requirements.txt      # Python bağımlılıkları
```

## 🔧 Özellikler

- ✅ PDF dekont yükleme
- ✅ Otomatik dekont analizi (Gemini AI)
- ✅ Admin paneli
- ✅ Başvuru takibi
- ✅ Otomatik kurulum scripti
- ✅ Systemd servis desteği

## 📝 Notlar

- API key'ler hardcoded olarak kodda bulunuyor
- Otomatik kurulum scripti tüm gerekli adımları yapıyor
- Systemd servisi otomatik olarak kuruluyor

## 🚀 Özellikler

- **Web Formu**: Kullanıcı dostu başvuru formu
- **PDF Yükleme**: Opsiyonel PDF dosyası yükleme
- **🤖 Gemini AI**: Otomatik dekont analizi
- **Veritabanı**: SQLite ile veri saklama
- **Loglama**: Detaylı işlem logları
- **Responsive**: Mobil uyumlu tasarım

## 📋 Gereksinimler

- Python 3.8+
- Flask
- SQLite3
- Gemini AI API Key (opsiyonel)

## 🎯 Kullanım

### Başvuru Formu
- Ana sayfada başvuru formunu doldurun
- PDF dekont yükleyebilirsiniz (opsiyonel)
- **🤖 Gemini AI otomatik olarak dekontu analiz eder**
- Form gönderildikten sonra veriler veritabanına kaydedilir

### Admin Paneli
- `/admin/login` ile giriş yapın (kullanıcı: admin, şifre: admin123)
- Başvuruları, öğrencileri ve ödemeleri yönetin
- **Dekont Analizleri** sayfasından AI analizlerini görüntüleyin

### Başvuru Listesi
- `/basvurular` sayfasından tüm başvuruları görüntüleyebilirsiniz
- Başvurular tarih sırasına göre listelenir

## 🔧 Geliştirme

### Yeni Özellik Ekleme
1. `src/models/` altında yeni modeller oluşturun
2. `src/core/database.py`'de veritabanı işlemlerini ekleyin
3. `web/app.py`'de yeni route'lar ekleyin
4. `web/templates/` altında yeni sayfalar oluşturun

### Loglama
- Tüm işlemler `logs/` klasöründe loglanır
- Log seviyeleri: INFO, WARNING, ERROR

## 📊 Veritabanı

SQLite veritabanı `data/basvurular.db` dosyasında saklanır.

**Tablolar:**
- `basvurular`: Başvuru bilgileri
- `dekont_analizleri`: AI dekont analizleri
- `adminler`: Admin kullanıcıları
- `ogrenciler`: Öğrenci bilgileri
- `seviye_kayitlari`: Öğrenci seviyeleri
- `odemeler`: Ödeme kayıtları

## 🚨 Güvenlik

- Form verileri doğrulanır ve temizlenir
- Dosya yükleme güvenliği sağlanır
- SQL injection koruması
- XSS koruması
- AI analizi güvenliği

## 📝 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

---

**Geliştirici:** Kafka Proje Takımı  
**Versiyon:** 1.0  
**Son Güncelleme:** 2024 