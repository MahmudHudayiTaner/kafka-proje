"""
Başvuru veri modeli
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class BasvuruDurumu(Enum):
    """Başvuru durumları"""
    BEKLEMEDE = "beklemede"
    ISLENIYOR = "işleniyor"
    TAMAMLANDI = "tamamlandı"
    HATA = "hata"
    IPTAL = "iptal"


@dataclass
class Basvuru:
    """Başvuru veri modeli"""
    
    # Temel bilgiler
    ad: str
    soyad: str
    telefon: str
    eposta: str
    basvurulan_kur: str
    basvuru_tarihi: datetime
    
    # PDF bilgileri
    pdf_dosya_yolu: Optional[str] = None
    pdf_icerik: Optional[str] = None
    
    # AI analiz sonucu
    ai_analiz_sonucu: Optional[str] = None
    
    # Sistem bilgileri
    id: Optional[int] = None
    durum: BasvuruDurumu = BasvuruDurumu.BEKLEMEDE
    olusturma_tarihi: Optional[datetime] = None
    guncelleme_tarihi: Optional[datetime] = None
    
    def __post_init__(self):
        """Veri doğrulama"""
        if not self.ad or not self.ad.strip():
            raise ValueError("Ad alanı boş olamaz")
        
        if not self.soyad or not self.soyad.strip():
            raise ValueError("Soyad alanı boş olamaz")
        
        if not self.telefon or not self.telefon.strip():
            raise ValueError("Telefon alanı boş olamaz")
        
        if not self.eposta or not self.eposta.strip():
            raise ValueError("E-posta alanı boş olamaz")
        
        if not self.basvurulan_kur or not self.basvurulan_kur.strip():
            raise ValueError("Başvurulan kur alanı boş olamaz")
    
    def to_dict(self) -> Dict[str, Any]:
        """Sözlük formatına çevir"""
        return {
            'id': self.id,
            'ad': self.ad,
            'soyad': self.soyad,
            'telefon': self.telefon,
            'eposta': self.eposta,
            'basvurulan_kur': self.basvurulan_kur,
            'basvuru_tarihi': self.basvuru_tarihi.isoformat() if self.basvuru_tarihi else None,
            'pdf_dosya_yolu': self.pdf_dosya_yolu,
            'pdf_icerik': self.pdf_icerik,
            'ai_analiz_sonucu': self.ai_analiz_sonucu,
            'durum': self.durum.value,
            'olusturma_tarihi': self.olusturma_tarihi.isoformat() if self.olusturma_tarihi else None,
            'guncelleme_tarihi': self.guncelleme_tarihi.isoformat() if self.guncelleme_tarihi else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Basvuru':
        """Sözlükten oluştur"""
        # Tarih alanlarını parse et
        basvuru_tarihi = None
        if data.get('basvuru_tarihi'):
            if isinstance(data['basvuru_tarihi'], str):
                basvuru_tarihi = datetime.fromisoformat(data['basvuru_tarihi'])
            else:
                basvuru_tarihi = data['basvuru_tarihi']
        
        olusturma_tarihi = None
        if data.get('olusturma_tarihi'):
            if isinstance(data['olusturma_tarihi'], str):
                olusturma_tarihi = datetime.fromisoformat(data['olusturma_tarihi'])
            else:
                olusturma_tarihi = data['olusturma_tarihi']
        
        guncelleme_tarihi = None
        if data.get('guncelleme_tarihi'):
            if isinstance(data['guncelleme_tarihi'], str):
                guncelleme_tarihi = datetime.fromisoformat(data['guncelleme_tarihi'])
            else:
                guncelleme_tarihi = data['guncelleme_tarihi']
        
        # Durum enum'ını parse et
        durum = BasvuruDurumu.BEKLEMEDE
        if data.get('durum'):
            try:
                durum = BasvuruDurumu(data['durum'])
            except ValueError:
                pass
        
        # basvuru_tarihi zorunlu alan, None olamaz
        if not basvuru_tarihi:
            raise ValueError("Başvuru tarihi zorunludur")
        
        return cls(
            id=data.get('id'),
            ad=data['ad'],
            soyad=data['soyad'],
            telefon=data['telefon'],
            eposta=data['eposta'],
            basvurulan_kur=data['basvurulan_kur'],
            basvuru_tarihi=basvuru_tarihi,
            pdf_dosya_yolu=data.get('pdf_dosya_yolu'),
            pdf_icerik=data.get('pdf_icerik'),
            ai_analiz_sonucu=data.get('ai_analiz_sonucu'),
            durum=durum,
            olusturma_tarihi=olusturma_tarihi,
            guncelleme_tarihi=guncelleme_tarihi
        )
    
    def tam_ad(self) -> str:
        """Tam ad getir"""
        return f"{self.ad} {self.soyad}".strip()
    
    def durum_guncelle(self, yeni_durum: BasvuruDurumu) -> None:
        """Durum güncelle"""
        self.durum = yeni_durum
        self.guncelleme_tarihi = datetime.now()
    
    def pdf_ekle(self, dosya_yolu: str, icerik: Optional[str] = None) -> None:
        """PDF bilgilerini ekle"""
        self.pdf_dosya_yolu = dosya_yolu
        self.pdf_icerik = icerik
        self.guncelleme_tarihi = datetime.now()
    
    def ai_analiz_ekle(self, analiz_sonucu: str) -> None:
        """AI analiz sonucunu ekle"""
        self.ai_analiz_sonucu = analiz_sonucu
        self.guncelleme_tarihi = datetime.now()
    
    def __str__(self) -> str:
        """String temsili"""
        return f"Başvuru(id={self.id}, ad={self.tam_ad()}, durum={self.durum.value})"
    
    def __repr__(self) -> str:
        """Repr temsili"""
        return self.__str__() 