"""
Veritabanı işlemleri
"""
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from .config import get_config
from .logger import get_logger


class DatabaseManager:
    """SQLite veritabanı yöneticisi"""
    
    def __init__(self, db_path: Optional[str] = None):
        config = get_config()
        self.db_path = db_path or config.get_database_path()
        self.logger = get_logger(__name__)
        self._ensure_db_directory()
        self._create_tables()
    
    def _ensure_db_directory(self) -> None:
        """Veritabanı dizininin varlığını kontrol et"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        self.logger.info("Veritabanı tabloları oluşturuluyor...")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Başvurular tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS basvurular (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad TEXT NOT NULL,
                    soyad TEXT NOT NULL,
                    telefon TEXT NOT NULL,
                    eposta TEXT NOT NULL,
                    basvurulan_kur TEXT NOT NULL,
                    basvuru_tarihi DATE NOT NULL,
                    pdf_dosya_yolu TEXT,
                    pdf_icerik TEXT,
                    ai_analiz_sonucu TEXT,
                    islenme_durumu TEXT DEFAULT 'beklemede',
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Log tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS islem_loglari (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    islem_tipi TEXT NOT NULL,
                    islem_detayi TEXT,
                    durum TEXT NOT NULL,
                    hata_mesaji TEXT,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            self.logger.info("Veritabanı tabloları başarıyla oluşturuldu")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı al"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Dict-like access
        return conn
    
    def basvuru_ekle(self, basvuru_data: Dict[str, Any]) -> int:
        """Yeni başvuru ekle"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO basvurular 
                    (ad, soyad, telefon, eposta, basvurulan_kur, basvuru_tarihi, 
                     pdf_dosya_yolu, pdf_icerik, ai_analiz_sonucu)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    basvuru_data.get('ad'),
                    basvuru_data.get('soyad'),
                    basvuru_data.get('telefon'),
                    basvuru_data.get('eposta'),
                    basvuru_data.get('basvurulan_kur'),
                    basvuru_data.get('basvuru_tarihi'),
                    basvuru_data.get('pdf_dosya_yolu'),
                    basvuru_data.get('pdf_icerik'),
                    basvuru_data.get('ai_analiz_sonucu')
                ))
                
                basvuru_id = cursor.lastrowid
                conn.commit()
                
                if basvuru_id is None:
                    raise RuntimeError("Başvuru ID alınamadı")
                
                self.logger.info(f"Başvuru eklendi: ID={basvuru_id}, Ad={basvuru_data.get('ad')} {basvuru_data.get('soyad')}")
                return basvuru_id
                
        except Exception as e:
            self.logger.error(f"Başvuru eklenirken hata: {e}")
            raise
    
    def basvuru_guncelle(self, basvuru_id: int, guncelleme_data: Dict[str, Any]) -> bool:
        """Başvuru güncelle"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Güncellenecek alanları hazırla
                update_fields = []
                values = []
                
                for key, value in guncelleme_data.items():
                    if key in ['ad', 'soyad', 'telefon', 'eposta', 'basvurulan_kur', 
                              'basvuru_tarihi', 'pdf_dosya_yolu', 'pdf_icerik', 
                              'ai_analiz_sonucu', 'islenme_durumu']:
                        update_fields.append(f"{key} = ?")
                        values.append(value)
                
                if not update_fields:
                    return False
                
                values.append(datetime.now())
                values.append(basvuru_id)
                
                query = f"""
                    UPDATE basvurular 
                    SET {', '.join(update_fields)}, guncelleme_tarihi = ?
                    WHERE id = ?
                """
                
                cursor.execute(query, values)
                conn.commit()
                
                self.logger.info(f"Başvuru güncellendi: ID={basvuru_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Başvuru güncellenirken hata: {e}")
            raise
    
    def basvuru_getir(self, basvuru_id: int) -> Optional[Dict[str, Any]]:
        """Başvuru getir"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM basvurular WHERE id = ?
                """, (basvuru_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            self.logger.error(f"Başvuru getirilirken hata: {e}")
            raise
    
    def basvurulari_listele(self, durum: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Başvuruları listele"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM basvurular"
                params = []
                
                if durum:
                    query += " WHERE islenme_durumu = ?"
                    params.append(durum)
                
                query += " ORDER BY olusturma_tarihi DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Başvurular listelenirken hata: {e}")
            raise
    
    def islem_logu_ekle(self, islem_tipi: str, islem_detayi: str, 
                        durum: str, hata_mesaji: Optional[str] = None) -> None:
        """İşlem logu ekle"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO islem_loglari 
                    (islem_tipi, islem_detayi, durum, hata_mesaji)
                    VALUES (?, ?, ?, ?)
                """, (islem_tipi, islem_detayi, durum, hata_mesaji))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"İşlem logu eklenirken hata: {e}")
    
    def istatistikler_getir(self) -> Dict[str, Any]:
        """Veritabanı istatistiklerini getir"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Toplam başvuru sayısı
                cursor.execute("SELECT COUNT(*) FROM basvurular")
                toplam_basvuru = cursor.fetchone()[0]
                
                # Durum bazında sayılar
                cursor.execute("""
                    SELECT islenme_durumu, COUNT(*) 
                    FROM basvurular 
                    GROUP BY islenme_durumu
                """)
                durum_sayilari = dict(cursor.fetchall())
                
                # Son 7 günlük başvuru sayısı
                cursor.execute("""
                    SELECT COUNT(*) FROM basvurular 
                    WHERE olusturma_tarihi >= date('now', '-7 days')
                """)
                son_7_gun = cursor.fetchone()[0]
                
                return {
                    'toplam_basvuru': toplam_basvuru,
                    'durum_sayilari': durum_sayilari,
                    'son_7_gun': son_7_gun
                }
                
        except Exception as e:
            self.logger.error(f"İstatistikler getirilirken hata: {e}")
            raise


# Singleton instance
_db_instance = None

def get_database() -> DatabaseManager:
    """Database instance'ı al"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance 