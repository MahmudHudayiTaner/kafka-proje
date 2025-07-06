# Kafka Proje - Başvuru Sistemi

Basit ve kullanışlı bir web tabanlı başvuru formu sistemi.

## 🚀 Özellikler

- **Web Formu**: Kullanıcı dostu başvuru formu
- **PDF Yükleme**: Opsiyonel PDF dosyası yükleme
- **Veritabanı**: SQLite ile veri saklama
- **Loglama**: Detaylı işlem logları
- **Responsive**: Mobil uyumlu tasarım

## 📋 Gereksinimler

- Python 3.8+
- Flask
- SQLite3

## 🛠️ Kurulum

1. **Projeyi klonlayın:**
```bash
git clone <repo-url>
cd "Kafka Proje"
```

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Uygulamayı başlatın:**
```bash
python run_web.py
```

4. **Tarayıcıda açın:**
```
http://localhost:5000
```

## 📁 Proje Yapısı

```
Kafka Proje/
├── data/                   # Veritabanı dosyaları
├── logs/                   # Log dosyaları
├── src/                    # Kaynak kodlar
│   ├── core/              # Temel modüller
│   ├── models/            # Veri modelleri
│   └── utils/             # Yardımcı fonksiyonlar
├── web/                   # Web uygulaması
│   ├── static/            # CSS, JS dosyaları
│   ├── templates/         # HTML şablonları
│   └── uploads/           # Yüklenen dosyalar
├── requirements.txt        # Python bağımlılıkları
└── run_web.py            # Başlatıcı script
```

## 🎯 Kullanım

### Başvuru Formu
- Ana sayfada başvuru formunu doldurun
- PDF dosyası yükleyebilirsiniz (opsiyonel)
- Form gönderildikten sonra veriler veritabanına kaydedilir

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

## 🚨 Güvenlik

- Form verileri doğrulanır ve temizlenir
- Dosya yükleme güvenliği sağlanır
- SQL injection koruması

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