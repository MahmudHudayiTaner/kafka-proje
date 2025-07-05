"""
Bu script, Gmail'den "Başvuru Formu" başlıklı okunmamış mailleri alır
ve form verilerini bir SQLite veritabanına kaydeder.
"""

# ---------------------
# 📦 Kütüphane Importları
# ---------------------
import time
import imaplib
import email
import sqlite3
import pandas as pd
from email.header import decode_header
from openpyxl import load_workbook

# ---------------------
# ⚙️ Config ve Ayarlar
# ---------------------
CONFIG_PATH = "config.xlsx"

def excel_to_dict(excel_path):
    df = pd.read_excel(excel_path, engine='openpyxl')
    return dict(zip(df['Name'], df['Value']))

config = excel_to_dict(CONFIG_PATH)

EMAIL = config["mail"]
PASSWORD = config["mail_app_password"]
IMAP_SERVER = config["imap_server"]
DB_YOLU = config["db"]

# ---------------------
# 📬 Mail İşlemleri
# ---------------------
def mail_baglanti_ac():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")
    return mail

def inbox_basvuru_maillerini_cek(mail):
    query = '(UNSEEN SUBJECT "Basvuru Formu")'.encode('utf-8')
    status, messages = mail.uid('SEARCH', 'CHARSET', 'UTF-8', query)

    if status != 'OK' or messages == [b'']:
        return []

    return messages[0].split()

def mail_veri_getir(mail, uid):
    _, msg_data = mail.uid('fetch', uid, '(RFC822)')
    return email.message_from_bytes(msg_data[0][1])

def get_subject(msg):
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        return subject.decode(encoding or "utf-8", errors="ignore")
    return subject

def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""

# ---------------------
# 🧩 Veri İşleme
# ---------------------
def parse_body(body):
    bilgiler = {
        "Ad": "",
        "Soyad": "",
        "Telefon": "",
        "Eposta": "",
        "Başvurulan Kur": "",
        "Başvuru Tarihi": ""
    }
    for satir in body.splitlines():
        for key in bilgiler:
            if satir.lower().startswith(key.lower()):
                _, deger = satir.split(":", 1)
                bilgiler[key] = deger.strip()
    return bilgiler

def mail_veri_ayir(msg):
    body = get_body(msg)
    bilgiler = parse_body(body)

    if not any(bilgiler.values()):
        raise ValueError("Parse edilen bilgiler boş!")

    return bilgiler

# ---------------------
# 🗃️ Veritabanı İşlemleri
# ---------------------
def db_yaz(db_yolu, tablo_adi, bilgi):
    conn = sqlite3.connect(db_yolu)
    cur = conn.cursor()

    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {tablo_adi} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad TEXT,
        soyad TEXT,
        telefon TEXT,
        eposta TEXT,
        basvurulan_kur TEXT,
        basvuru_tarihi TEXT
    )
    """)

    cur.execute(f"""
    INSERT INTO {tablo_adi} 
    (ad, soyad, telefon, eposta, basvurulan_kur, basvuru_tarihi)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        bilgi.get('Ad', ''),
        bilgi.get('Soyad', ''),
        bilgi.get('Telefon', ''),
        bilgi.get('Eposta', ''),
        bilgi.get('Başvurulan Kur', ''),
        bilgi.get('Başvuru Tarihi', '')
    ))

    conn.commit()
    conn.close()
    print(f"{bilgi.get('Ad')} {bilgi.get('Soyad')} SQLite'a kaydedildi.")

# ---------------------
# 🚀 Ana Uygulama
# ---------------------
def main():
    try:
        mail = mail_baglanti_ac()
        mail_ids = inbox_basvuru_maillerini_cek(mail)

        if not mail_ids:
            print("📭 İşlenecek mail bulunamadı.")
            return

        for uid in mail_ids:
            try:
                msg = mail_veri_getir(mail, uid)
                veri = mail_veri_ayir(msg)
                db_yaz(DB_YOLU, "gelenbasvurular", veri)
                mail.uid('store', uid, '+FLAGS', '\\Seen')
            except Exception as e:
                print(f"❌ Hata oluştu: {e}")
                mail.uid('store', uid, '-FLAGS', '\\Seen')

    finally:
        mail.logout()
        print("📤 Oturum kapatıldı.")

# ---------------------
# ▶️ Çalıştır
# ---------------------
if __name__ == "__main__":
    main()
