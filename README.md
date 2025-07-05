# Kafka Proje - Gelen Başvurular Otomasyonu

Bu proje, Gmail'den "Başvuru Formu" başlıklı okunmamış mailleri otomatik olarak alır ve form verilerini SQLite veritabanına kaydeder.

## 🚀 Özellikler

- Gmail IMAP bağlantısı ile mail okuma
- "Başvuru Formu" başlıklı mailleri otomatik tespit
- Mail içeriğinden form verilerini parse etme
- SQLite veritabanına otomatik kaydetme
- Okunan mailleri "okundu" olarak işaretleme

## 📋 Gereksinimler

```bash
pip install pandas openpyxl
```

## ⚙️ Kurulum

1. Projeyi klonlayın:
```bash
git clone <repository-url>
cd kafka-proje
```

2. `config.xlsx` dosyasını oluşturun ve aşağıdaki bilgileri ekleyin:
   - `mail`: Gmail adresiniz
   - `mail_app_password`: Gmail uygulama şifreniz
   - `imap_server`: IMAP sunucu adresi (genellikle imap.gmail.com)
   - `db`: SQLite veritabanı dosya yolu

3. Gmail'de "2 Adımlı Doğrulama"yı etkinleştirin ve bir uygulama şifresi oluşturun.

## 🎯 Kullanım

```bash
python GelenBasvurularOtomasyon.py
```

## 📁 Proje Yapısı

```
Kafka Proje/
├── GelenBasvurularOtomasyon.py  # Ana uygulama
├── GelenDekontlarOtomasyon.py   # Dekont işleme
├── pdf.py                        # PDF işleme
├── sqlite.py                     # Veritabanı işlemleri
├── config.xlsx                   # Konfigürasyon dosyası
├── db_kafka.db                   # SQLite veritabanı
└── README.md                     # Bu dosya
```

## 🔧 Konfigürasyon

`config.xlsx` dosyasında aşağıdaki ayarları yapın:

| Name | Value |
|------|-------|
| mail | your-email@gmail.com |
| mail_app_password | your-app-password |
| imap_server | imap.gmail.com |
| db | db_kafka.db |

## 📊 Veritabanı Şeması

Başvuru verileri `gelenbasvurular` tablosunda saklanır:

- `id`: Otomatik artan ID
- `ad`: Başvuru sahibinin adı
- `soyad`: Başvuru sahibinin soyadı
- `telefon`: Telefon numarası
- `eposta`: E-posta adresi
- `basvurulan_kur`: Başvuru yapılan kurum
- `basvuru_tarihi`: Başvuru tarihi

## 🤝 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. 