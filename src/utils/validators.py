"""
Veri doğrulama fonksiyonları
"""
import re
from typing import Optional, Tuple
from datetime import datetime


class ValidationError(Exception):
    """Doğrulama hatası"""
    pass


def validate_email(email: str) -> bool:
    """E-posta adresi doğrula"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Telefon numarası doğrula (Türkiye formatı)"""
    # Türkiye telefon numarası formatları
    patterns = [
        r'^\+90[0-9]{10}$',  # +905551234567
        r'^0[0-9]{10}$',      # 05551234567
        r'^[0-9]{10}$',       # 5551234567
        r'^\+90\s[0-9]{3}\s[0-9]{3}\s[0-9]{2}\s[0-9]{2}$',  # +90 555 123 45 67
        r'^0[0-9]{3}\s[0-9]{3}\s[0-9]{2}\s[0-9]{2}$'        # 0555 123 45 67
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone):
            return True
    return False


def validate_turkish_name(name: str) -> bool:
    """Türkçe isim doğrula"""
    # Türkçe karakterler ve boşluk
    pattern = r'^[a-zA-ZğüşıöçĞÜŞİÖÇ\s]+$'
    return bool(re.match(pattern, name.strip())) and len(name.strip()) >= 2


def validate_date(date_str: str) -> Optional[datetime]:
    """Tarih formatı doğrula"""
    date_formats = [
        '%Y-%m-%d',
        '%d.%m.%Y',
        '%d/%m/%Y',
        '%Y/%m/%d'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def validate_pdf_file(file_path: str) -> bool:
    """PDF dosyası doğrula"""
    import os
    from pathlib import Path
    
    if not os.path.exists(file_path):
        return False
    
    path_obj = Path(file_path)
    return path_obj.suffix.lower() == '.pdf' and path_obj.stat().st_size > 0


def validate_basvuru_data(data: dict) -> Tuple[bool, Optional[str]]:
    """Başvuru verilerini doğrula"""
    try:
        # Zorunlu alanları kontrol et
        required_fields = ['ad', 'soyad', 'telefon', 'eposta', 'basvurulan_kur', 'basvuru_tarihi']
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Zorunlu alan eksik: {field}"
        
        # İsim doğrulama
        if not validate_turkish_name(data['ad']):
            return False, "Geçersiz ad formatı"
        
        if not validate_turkish_name(data['soyad']):
            return False, "Geçersiz soyad formatı"
        
        # E-posta doğrulama
        if not validate_email(data['eposta']):
            return False, "Geçersiz e-posta formatı"
        
        # Telefon doğrulama
        if not validate_phone(data['telefon']):
            return False, "Geçersiz telefon numarası formatı"
        
        # Tarih doğrulama
        if isinstance(data['basvuru_tarihi'], str):
            if not validate_date(data['basvuru_tarihi']):
                return False, "Geçersiz tarih formatı"
        
        # PDF dosyası kontrolü (varsa)
        if 'pdf_dosya_yolu' in data and data['pdf_dosya_yolu']:
            if not validate_pdf_file(data['pdf_dosya_yolu']):
                return False, "Geçersiz PDF dosyası"
        
        return True, None
        
    except Exception as e:
        return False, f"Doğrulama hatası: {str(e)}"


def sanitize_phone(phone: str) -> str:
    """Telefon numarasını temizle ve standartlaştır"""
    # Sadece rakamları al
    digits = re.sub(r'[^\d]', '', phone)
    
    # Türkiye telefon numarası formatına çevir
    if len(digits) == 11 and digits.startswith('0'):
        return '+90' + digits[1:]
    elif len(digits) == 10:
        return '+90' + digits
    elif len(digits) == 12 and digits.startswith('90'):
        return '+' + digits
    
    return phone


def sanitize_name(name: str) -> str:
    """İsmi temizle ve standartlaştır"""
    # Fazla boşlukları temizle
    name = ' '.join(name.split())
    
    # İlk harfleri büyük yap
    return name.title()


def format_phone_for_display(phone: str) -> str:
    """Telefon numarasını görüntüleme formatına çevir"""
    # Sadece rakamları al
    digits = re.sub(r'[^\d]', '', phone)
    
    if len(digits) == 10:
        return f"{digits[:3]} {digits[3:6]} {digits[6:8]} {digits[8:]}"
    elif len(digits) == 11 and digits.startswith('0'):
        digits = digits[1:]
        return f"{digits[:3]} {digits[3:6]} {digits[6:8]} {digits[8:]}"
    
    return phone 