"""
SQLite veritabanı işlemleri
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

from .logger import get_logger
from .config import get_config

class Database:
    """SQLite veritabanı yöneticisi"""
    
    def __init__(self):
        config = get_config()
        self.db_path = config.get_database_path()
        self.logger = get_logger("database")
        self._init_database()
    
    def _init_database(self):
        """Veritabanını başlat"""
        try:
            # Data klasörünü oluştur
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Veritabanı bağlantısı
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Başvurular tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS basvurular (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ad TEXT NOT NULL,
                        soyad TEXT NOT NULL,
                        telefon TEXT NOT NULL,
                        eposta TEXT,
                        dogum_tarihi DATE,
                        cinsiyet TEXT,
                        adres TEXT,
                        kur_seviyesi TEXT NOT NULL,
                        basvuru_tarihi DATETIME NOT NULL,
                        pdf_dosya_yolu TEXT,
                        pdf_icerik TEXT,
                        ai_analiz_sonucu TEXT,
                        durum TEXT DEFAULT 'beklemede',
                        olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Admin tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS adminler (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Öğrenciler tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ogrenciler (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ad TEXT NOT NULL,
                        soyad TEXT NOT NULL,
                        telefon TEXT NOT NULL,
                        eposta TEXT,
                        aktif_seviye TEXT,
                        toplam_seviye_sayisi INTEGER DEFAULT 0,
                        toplam_odenen DECIMAL(10,2) DEFAULT 0,
                        durum TEXT DEFAULT 'aktif',
                        kayit_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
                        guncelleme_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Seviye kayıtları tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS seviye_kayitlari (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ogrenci_id INTEGER NOT NULL,
                        seviye TEXT NOT NULL,
                        baslama_tarihi DATETIME NOT NULL,
                        bitis_tarihi DATETIME,
                        durum TEXT DEFAULT 'aktif',
                        ucret DECIMAL(10,2) NOT NULL,
                        odenen_miktar DECIMAL(10,2) DEFAULT 0,
                        kalan_miktar DECIMAL(10,2) NOT NULL,
                        olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (ogrenci_id) REFERENCES ogrenciler (id)
                    )
                ''')
                
                # Ödemeler tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS odemeler (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ogrenci_id INTEGER NOT NULL,
                        seviye_id INTEGER NOT NULL,
                        odeme_tipi TEXT NOT NULL,
                        miktar DECIMAL(10,2) NOT NULL,
                        odeme_tarihi DATETIME,
                        dekont_yolu TEXT,
                        durum TEXT DEFAULT 'beklemede',
                        aciklama TEXT,
                        olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (ogrenci_id) REFERENCES ogrenciler (id),
                        FOREIGN KEY (seviye_id) REFERENCES seviye_kayitlari (id)
                    )
                ''')
                
                # Dekont analizleri tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS dekont_analizleri (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        basvuru_id INTEGER NOT NULL,
                        pdf_dosya_yolu TEXT NOT NULL,
                        sender_name TEXT,
                        amount DECIMAL(10,2),
                        bank_name TEXT,
                        transaction_date DATE,
                        transaction_time TIME,
                        extraction_date DATETIME NOT NULL,
                        raw_text TEXT,
                        confidence_score DECIMAL(3,2) DEFAULT 0.0,
                        olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (basvuru_id) REFERENCES basvurular (id)
                    )
                ''')
                
                conn.commit()
                self.logger.info("Veritabanı başarıyla başlatıldı")
                
                # Varsayılan admin kullanıcısını oluştur
                self._create_default_admin()
                
        except Exception as e:
            self.logger.error(f"Veritabanı başlatma hatası: {e}")
            raise
    
    def _create_default_admin(self):
        """Varsayılan admin kullanıcısını oluştur"""
        try:
            from src.models.admin import Admin
            
            # Varsayılan admin bilgileri
            default_username = "admin"
            default_password = "admin123"
            
            # Admin var mı kontrol et
            existing_admin = self.admin_get_by_username(default_username)
            if existing_admin:
                return
            
            # Yeni admin oluştur
            password_hash = Admin.hash_password(default_password)
            admin_data = {
                'username': default_username,
                'password_hash': password_hash,
                'is_active': True
            }
            
            self.admin_ekle(admin_data)
            self.logger.info(f"Varsayılan admin kullanıcısı oluşturuldu: {default_username}")
            
        except Exception as e:
            self.logger.error(f"Varsayılan admin oluşturma hatası: {e}")
    
    # Admin işlemleri
    def admin_ekle(self, admin_data: Dict[str, Any]) -> Optional[int]:
        """Yeni admin ekle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO adminler 
                    (username, password_hash, is_active)
                    VALUES (?, ?, ?)
                ''', (
                    admin_data['username'],
                    admin_data['password_hash'],
                    admin_data.get('is_active', True)
                ))
                
                admin_id = cursor.lastrowid
                conn.commit()
                
                self.logger.info(f"Admin eklendi: ID={admin_id}, Username={admin_data['username']}")
                return admin_id
                
        except Exception as e:
            self.logger.error(f"Admin ekleme hatası: {e}")
            return None
    
    def admin_get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Kullanıcı adına göre admin getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM adminler WHERE username = ? AND is_active = 1
                ''', (username,))
                
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                
                return None
                
        except Exception as e:
            self.logger.error(f"Admin getirme hatası: {e}")
            return None
    
    def admin_verify_password(self, username: str, password: str) -> bool:
        """Admin şifre doğrulama"""
        try:
            from src.models.admin import Admin
            
            admin_data = self.admin_get_by_username(username)
            if not admin_data:
                return False
            
            return Admin.verify_password(password, admin_data['password_hash'])
            
        except Exception as e:
            self.logger.error(f"Admin şifre doğrulama hatası: {e}")
            return False
    
    # Başvuru işlemleri
    def basvuru_ekle(self, basvuru_data: Dict[str, Any]) -> Optional[int]:
        """Yeni başvuru ekle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Email kontrolü - aynı email ile daha önce başvuru yapılmış mı?
                if basvuru_data.get('eposta'):
                    cursor.execute('''
                        SELECT id FROM basvurular WHERE eposta = ? AND eposta != ''
                    ''', (basvuru_data['eposta'],))
                    
                    if cursor.fetchone():
                        self.logger.warning(f"Bu email ile daha önce başvuru yapılmış: {basvuru_data['eposta']}")
                        return None
                
                cursor.execute('''
                    INSERT INTO basvurular 
                    (ad, soyad, telefon, eposta, dogum_tarihi, cinsiyet, adres, kur_seviyesi, basvuru_tarihi, 
                     pdf_dosya_yolu, pdf_icerik, ai_analiz_sonucu, durum)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    basvuru_data['ad'],
                    basvuru_data['soyad'],
                    basvuru_data['telefon'],
                    basvuru_data.get('eposta'),
                    basvuru_data.get('dogum_tarihi'),
                    basvuru_data.get('cinsiyet'),
                    basvuru_data.get('adres'),
                    basvuru_data['kur_seviyesi'],
                    basvuru_data['basvuru_tarihi'],
                    basvuru_data.get('pdf_dosya_yolu'),
                    basvuru_data.get('pdf_icerik'),
                    basvuru_data.get('ai_analiz_sonucu'),
                    'beklemede'
                ))
                
                basvuru_id = cursor.lastrowid
                conn.commit()
                
                self.logger.info(f"Başvuru eklendi: ID={basvuru_id}")
                return basvuru_id
                
        except Exception as e:
            self.logger.error(f"Başvuru ekleme hatası: {e}")
            return None
    
    def basvuru_getir(self, basvuru_id: int) -> Optional[Dict[str, Any]]:
        """Başvuru getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM basvurular WHERE id = ?
                ''', (basvuru_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                
                return None
                
        except Exception as e:
            self.logger.error(f"Başvuru getirme hatası: {e}")
            return None
    
    def basvurulari_listele(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Başvuruları listele"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM basvurular 
                    ORDER BY olusturma_tarihi DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Başvuru listeleme hatası: {e}")
            return []
    
    def basvuru_sil(self, basvuru_id: int) -> bool:
        """Başvuru sil"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM basvurular WHERE id = ?
                ''', (basvuru_id,))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Başvuru silindi: ID={basvuru_id}")
                    return True
                else:
                    self.logger.warning(f"Silinecek başvuru bulunamadı: ID={basvuru_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Başvuru silme hatası: {e}")
            return False
    
    def basvuru_guncelle(self, basvuru_id: int, basvuru_data: Dict[str, Any]) -> bool:
        """Başvuru güncelle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE basvurular SET
                    ad = ?, soyad = ?, telefon = ?, eposta = ?, 
                    kur_seviyesi = ?, basvuru_tarihi = ?,
                    pdf_dosya_yolu = ?, pdf_icerik = ?, ai_analiz_sonucu = ?
                    WHERE id = ?
                ''', (
                    basvuru_data['ad'],
                    basvuru_data['soyad'],
                    basvuru_data['telefon'],
                    basvuru_data.get('eposta'),
                    basvuru_data['kur_seviyesi'],
                    basvuru_data['basvuru_tarihi'],
                    basvuru_data.get('pdf_dosya_yolu'),
                    basvuru_data.get('pdf_icerik'),
                    basvuru_data.get('ai_analiz_sonucu'),
                    basvuru_id
                ))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Başvuru güncellendi: ID={basvuru_id}")
                    return True
                else:
                    self.logger.warning(f"Güncellenecek başvuru bulunamadı: ID={basvuru_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Başvuru güncelleme hatası: {e}")
            return False

    # Öğrenci işlemleri
    def ogrenci_ekle(self, ogrenci_data: Dict[str, Any]) -> Optional[int]:
        """Yeni öğrenci ekle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO ogrenciler 
                    (ad, soyad, telefon, eposta, aktif_seviye, toplam_seviye_sayisi, durum)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ogrenci_data['ad'],
                    ogrenci_data['soyad'],
                    ogrenci_data['telefon'],
                    ogrenci_data.get('eposta'),
                    ogrenci_data.get('aktif_seviye'),
                    ogrenci_data.get('toplam_seviye_sayisi', 1),
                    ogrenci_data.get('durum', 'aktif')
                ))
                
                ogrenci_id = cursor.lastrowid
                conn.commit()
                
                self.logger.info(f"Öğrenci eklendi: ID={ogrenci_id}")
                return ogrenci_id
                
        except Exception as e:
            self.logger.error(f"Öğrenci ekleme hatası: {e}")
            return None
    
    def ogrenci_getir(self, ogrenci_id: int) -> Optional[Dict[str, Any]]:
        """Öğrenci getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM ogrenciler WHERE id = ?
                ''', (ogrenci_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                
                return None
                
        except Exception as e:
            self.logger.error(f"Öğrenci getirme hatası: {e}")
            return None
    
    def ogrencileri_listele(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Öğrencileri listele"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM ogrenciler 
                    ORDER BY kayit_tarihi DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Öğrenci listeleme hatası: {e}")
            return []

    # Seviye işlemleri
    def seviye_kaydi_ekle(self, seviye_data: Dict[str, Any]) -> Optional[int]:
        """Yeni seviye kaydı ekle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO seviye_kayitlari 
                    (ogrenci_id, seviye, baslama_tarihi, ucret, kalan_miktar)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    seviye_data['ogrenci_id'],
                    seviye_data['seviye'],
                    seviye_data['baslama_tarihi'],
                    seviye_data['ucret'],
                    seviye_data['kalan_miktar']
                ))
                
                seviye_id = cursor.lastrowid
                conn.commit()
                
                self.logger.info(f"Seviye kaydı eklendi: ID={seviye_id}")
                return seviye_id
                
        except Exception as e:
            self.logger.error(f"Seviye kaydı ekleme hatası: {e}")
            return None
    
    def seviye_kaydi_getir(self, seviye_id: int) -> Optional[Dict[str, Any]]:
        """Seviye kaydı getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM seviye_kayitlari WHERE id = ?
                ''', (seviye_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                
                return None
                
        except Exception as e:
            self.logger.error(f"Seviye kaydı getirme hatası: {e}")
            return None
    
    def ogrenci_seviyeleri_getir(self, ogrenci_id: int) -> List[Dict[str, Any]]:
        """Öğrencinin tüm seviyelerini getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM seviye_kayitlari 
                    WHERE ogrenci_id = ? 
                    ORDER BY baslama_tarihi DESC
                ''', (ogrenci_id,))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Öğrenci seviyeleri getirme hatası: {e}")
            return []

    # Ödeme işlemleri
    def odeme_ekle(self, odeme_data: Dict[str, Any]) -> Optional[int]:
        """Yeni ödeme ekle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO odemeler 
                    (ogrenci_id, seviye_id, odeme_tipi, miktar, dekont_yolu, durum, aciklama)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    odeme_data['ogrenci_id'],
                    odeme_data['seviye_id'],
                    odeme_data['odeme_tipi'],
                    odeme_data['miktar'],
                    odeme_data.get('dekont_yolu'),
                    odeme_data.get('durum', 'beklemede'),
                    odeme_data.get('aciklama')
                ))
                
                odeme_id = cursor.lastrowid
                conn.commit()
                
                self.logger.info(f"Ödeme eklendi: ID={odeme_id}")
                return odeme_id
                
        except Exception as e:
            self.logger.error(f"Ödeme ekleme hatası: {e}")
            return None
    
    def odeme_onayla(self, odeme_id: int) -> bool:
        """Ödemeyi onayla"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Ödemeyi getir
                cursor.execute('''
                    SELECT * FROM odemeler WHERE id = ?
                ''', (odeme_id,))
                
                odeme = cursor.fetchone()
                if not odeme:
                    return False
                
                # Ödeme durumunu güncelle
                cursor.execute('''
                    UPDATE odemeler SET durum = 'onaylandi', odeme_tarihi = ? WHERE id = ?
                ''', (datetime.now(), odeme_id))
                
                # Seviye kaydını güncelle
                cursor.execute('''
                    UPDATE seviye_kayitlari 
                    SET odenen_miktar = odenen_miktar + ?, kalan_miktar = kalan_miktar - ?
                    WHERE id = ?
                ''', (odeme[4], odeme[4], odeme[2]))  # miktar, miktar, seviye_id
                
                # Öğrenci toplam ödemesini güncelle
                cursor.execute('''
                    UPDATE ogrenciler 
                    SET toplam_odenen = toplam_odenen + ?, guncelleme_tarihi = ?
                    WHERE id = ?
                ''', (odeme[4], datetime.now(), odeme[1]))  # miktar, tarih, ogrenci_id
                
                conn.commit()
                self.logger.info(f"Ödeme onaylandı: ID={odeme_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Ödeme onaylama hatası: {e}")
            return False
    
    def odemeleri_listele(self, ogrenci_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Ödemeleri listele"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if ogrenci_id:
                    cursor.execute('''
                        SELECT o.*, sk.seviye, og.ad, og.soyad 
                        FROM odemeler o
                        JOIN seviye_kayitlari sk ON o.seviye_id = sk.id
                        JOIN ogrenciler og ON o.ogrenci_id = og.id
                        WHERE o.ogrenci_id = ?
                        ORDER BY o.olusturma_tarihi DESC
                        LIMIT ?
                    ''', (ogrenci_id, limit))
                else:
                    cursor.execute('''
                        SELECT o.*, sk.seviye, og.ad, og.soyad 
                        FROM odemeler o
                        JOIN seviye_kayitlari sk ON o.seviye_id = sk.id
                        JOIN ogrenciler og ON o.ogrenci_id = og.id
                        ORDER BY o.olusturma_tarihi DESC
                        LIMIT ?
                    ''', (limit,))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Ödeme listeleme hatası: {e}")
            return []
    
    # Dekont analizi işlemleri
    def dekont_analizi_ekle(self, analiz_data: Dict[str, Any]) -> Optional[int]:
        """Yeni dekont analizi ekle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO dekont_analizleri 
                    (basvuru_id, pdf_dosya_yolu, sender_name, amount, bank_name, 
                     transaction_date, transaction_time, extraction_date, raw_text, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    analiz_data['basvuru_id'],
                    analiz_data['pdf_dosya_yolu'],
                    analiz_data.get('sender_name'),
                    analiz_data.get('amount'),
                    analiz_data.get('bank_name'),
                    analiz_data.get('date'),
                    analiz_data.get('time'),
                    analiz_data['extraction_date'],
                    analiz_data.get('raw_text'),
                    analiz_data.get('confidence_score', 0.0)
                ))
                
                analiz_id = cursor.lastrowid
                conn.commit()
                
                self.logger.info(f"Dekont analizi eklendi: ID={analiz_id}, BasvuruID={analiz_data['basvuru_id']}")
                return analiz_id
                
        except Exception as e:
            self.logger.error(f"Dekont analizi ekleme hatası: {e}")
            return None
    
    def dekont_analizi_getir(self, analiz_id: int) -> Optional[Dict[str, Any]]:
        """Dekont analizi getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM dekont_analizleri WHERE id = ?
                ''', (analiz_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                
                return None
                
        except Exception as e:
            self.logger.error(f"Dekont analizi getirme hatası: {e}")
            return None
    
    def basvuru_dekont_analizi_getir(self, basvuru_id: int) -> Optional[Dict[str, Any]]:
        """Başvuruya ait dekont analizi getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM dekont_analizleri WHERE basvuru_id = ?
                    ORDER BY olusturma_tarihi DESC LIMIT 1
                ''', (basvuru_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                
                return None
                
        except Exception as e:
            self.logger.error(f"Başvuru dekont analizi getirme hatası: {e}")
            return None
    
    def dekont_analizleri_listele(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Dekont analizlerini listele"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT da.*, b.ad, b.soyad, b.telefon
                    FROM dekont_analizleri da
                    JOIN basvurular b ON da.basvuru_id = b.id
                    ORDER BY da.olusturma_tarihi DESC
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Dekont analizleri listeleme hatası: {e}")
            return []

# Singleton instance
_database_instance = None

def get_database() -> Database:
    """Database singleton instance'ını döndür"""
    global _database_instance
    if _database_instance is None:
        _database_instance = Database()
    return _database_instance 