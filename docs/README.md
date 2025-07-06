# Kafka Proje - Başvuru ve Öğrenci Yönetim Sistemi

## Genel Bakış
Bu proje, başvuru formlarının web üzerinden alınması, başvuruların ve öğrencilerin yönetilmesi, admin paneli ile işlemlerin kolayca takip edilmesi için geliştirilmiş bir Python/Flask tabanlı web uygulamasıdır.

## Özellikler
- Web tabanlı başvuru formu
- Başvuruların SQLite veritabanına kaydı
- Admin girişi ve paneli
- Başvuru, öğrenci ve ödeme yönetimi
- Dosya yükleme (PDF)
- Bootstrap ile modern ve responsive arayüz
- Test altyapısı (unittest)

## Klasör Yapısı
```
Kafka Proje/
├── config/                # (Kullanılmıyor, silinebilir)
├── data/                  # Veritabanı dosyası
├── deploy.py              # Production güncelleme scripti
├── docs/                  # Dokümantasyon
│   └── README.md          # (Bu dosya)
├── logs/                  # Log dosyaları
├── requirements.txt       # Bağımlılıklar
├── run_tests.py           # Test çalıştırıcı
├── run_web.py             # Web uygulaması başlatıcı
├── src/                   # Uygulama çekirdek kodları
│   ├── core/              # Veritabanı, logger, config
│   ├── models/            # Veri modelleri
│   └── utils/             # Doğrulama ve yardımcılar
├── temp/                  # (Kullanılmıyor, silinebilir)
├── tests/                 # Otomatik testler
├── uploads/               # (Kullanılmıyor, silinebilir)
└── web/                   # Web uygulaması ve şablonlar
    ├── app.py             # Flask uygulaması
    ├── static/            # Statik dosyalar (boşsa silinebilir)
    ├── templates/         # HTML şablonlar
    └── uploads/           # Kullanıcı yüklemeleri
```

## Kurulum
1. Gerekli Python paketlerini yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
2. Web uygulamasını başlatın:
   ```bash
   python run_web.py
   ```
3. Tarayıcıda [http://localhost:5000](http://localhost:5000) adresini açın.

## Admin Girişi
- Kullanıcı adı: **admin**
- Şifre: **admin123**

## Testler
Tüm testleri çalıştırmak için:
```bash
python run_tests.py
```
Detaylı bilgi için `TEST_GUIDE.md` dosyasına bakınız.

## Kullanılan Teknolojiler
- Python 3
- Flask
- SQLite
- Bootstrap
- Unittest

## Sıkça Sorulanlar
- **Veritabanı nerede?**
  - `data/basvurular.db` dosyasında tutulur.
- **Yedekleme nasıl yapılır?**
  - `deploy.py` scripti ile otomatik yedek alınabilir.
- **Kendi alanlarımı ekleyebilir miyim?**
  - Evet, model ve şablonları güncelleyerek yeni alanlar ekleyebilirsiniz.

## Katkı ve Geliştirme
- Kodlar modüler ve genişletilebilir yapıdadır.
- Yeni özellik eklemek için ilgili model, servis ve şablonları güncelleyin.
- Test eklemeyi unutmayın!

## Lisans
Bu proje eğitim ve demo amaçlıdır. 