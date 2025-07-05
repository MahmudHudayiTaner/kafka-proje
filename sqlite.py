import sqlite3

conn = sqlite3.connect("db_kafka.db")  # dosya yoksa oluşturur
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS gelenbasvurular (
    basvuru_tarihi TEXT,
    ad TEXT,
    soyad TEXT,
    telefon TEXT,
    eposta TEXT,
    basvurulan_kur TEXT
)
""")
conn.commit()


cur.execute("INSERT INTO gelenbasvurular (basvuru_tarihi, ad, soyad,telefon,eposta,basvurulan_kur) VALUES (?,?,?,?,?,?)", ("12/10/2025", "Ali","Kara","5337462288","partner@kayacantek.com","A1"))
conn.commit()


conn.close()
