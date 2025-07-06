"""
Başvuru modeli
"""
from datetime import datetime
from typing import Optional, Dict, Any

class Basvuru:
    """Başvuru veri modeli"""
    
    def __init__(self, 
                 ad: str,
                 soyad: str,
                 telefon: str,
                 eposta: Optional[str] = None,
                 dogum_tarihi: Optional[str] = None,
                 cinsiyet: Optional[str] = None,
                 adres: Optional[str] = None,
                 kur_seviyesi: str = "",
                 basvuru_tarihi: Optional[datetime] = None,
                 pdf_dosya_yolu: Optional[str] = None,
                 pdf_icerik: Optional[str] = None,
                 ai_analiz_sonucu: Optional[str] = None):
        
        self.ad = ad
        self.soyad = soyad
        self.telefon = telefon
        self.eposta = eposta
        self.dogum_tarihi = dogum_tarihi
        self.cinsiyet = cinsiyet
        self.adres = adres
        self.kur_seviyesi = kur_seviyesi
        self.basvuru_tarihi = basvuru_tarihi or datetime.now()
        self.pdf_dosya_yolu = pdf_dosya_yolu
        self.pdf_icerik = pdf_icerik
        self.ai_analiz_sonucu = ai_analiz_sonucu
    
    def tam_ad(self) -> str:
        """Tam ad döndür"""
        return f"{self.ad} {self.soyad}".strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary formatına çevir"""
        return {
            'ad': self.ad,
            'soyad': self.soyad,
            'telefon': self.telefon,
            'eposta': self.eposta,
            'dogum_tarihi': self.dogum_tarihi,
            'cinsiyet': self.cinsiyet,
            'adres': self.adres,
            'kur_seviyesi': self.kur_seviyesi,
            'basvuru_tarihi': self.basvuru_tarihi,
            'pdf_dosya_yolu': self.pdf_dosya_yolu,
            'pdf_icerik': self.pdf_icerik,
            'ai_analiz_sonucu': self.ai_analiz_sonucu
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Basvuru':
        """Dictionary'den Basvuru oluştur"""
        return cls(
            ad=data.get('ad', ''),
            soyad=data.get('soyad', ''),
            telefon=data.get('telefon', ''),
            eposta=data.get('eposta'),
            dogum_tarihi=data.get('dogum_tarihi'),
            cinsiyet=data.get('cinsiyet'),
            adres=data.get('adres'),
            kur_seviyesi=data.get('kur_seviyesi', ''),
            basvuru_tarihi=data.get('basvuru_tarihi'),
            pdf_dosya_yolu=data.get('pdf_dosya_yolu'),
            pdf_icerik=data.get('pdf_icerik'),
            ai_analiz_sonucu=data.get('ai_analiz_sonucu')
        )
    
    def __str__(self) -> str:
        return f"Başvuru({self.tam_ad()}, {self.telefon})"
    
    def __repr__(self) -> str:
        return self.__str__() 