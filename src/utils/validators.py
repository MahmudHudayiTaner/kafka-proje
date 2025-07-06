"""
Veri doğrulama fonksiyonları
"""
import re
from typing import Optional, Tuple, Dict, Any
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


def validate_pdf_file(file_path: str) -> Tuple[bool, str]:
    """
    PDF dosyasını doğrula (basit kontrol)
    
    Args:
        file_path: Dosya yolu
        
    Returns:
        (is_valid, error_message)
    """
    try:
        if not file_path or not file_path.lower().endswith('.pdf'):
            return False, "Sadece PDF dosyaları kabul edilir"
        
        # Dosya boyutu kontrolü (16MB)
        import os
        if os.path.getsize(file_path) > 16 * 1024 * 1024:
            return False, "Dosya boyutu 16MB'dan büyük olamaz"
        
        return True, ""
        
    except Exception as e:
        return False, f"Dosya kontrolü hatası: {str(e)}"


def validate_basvuru_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Başvuru verilerini doğrula
    
    Args:
        data: Doğrulanacak veri
        
    Returns:
        (is_valid, error_message)
    """
    # Ad kontrolü
    if not data.get('ad') or len(data['ad'].strip()) < 2:
        return False, "Ad en az 2 karakter olmalıdır"
    
    # Soyad kontrolü
    if not data.get('soyad') or len(data['soyad'].strip()) < 2:
        return False, "Soyad en az 2 karakter olmalıdır"
    
    # Telefon kontrolü
    phone = data.get('telefon', '').strip()
    if not phone:
        return False, "Telefon numarası gereklidir"
    
    # Basit telefon formatı kontrolü (Türkiye)
    phone_clean = re.sub(r'[^\d]', '', phone)
    if len(phone_clean) < 10:
        return False, "Geçerli bir telefon numarası giriniz"
    
    # E-posta kontrolü
    email = data.get('eposta', '').strip()
    if email:  # E-posta opsiyonel
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Geçerli bir e-posta adresi giriniz"
    
    # Kur seviyesi kontrolü
    if not data.get('kur_seviyesi') or len(data['kur_seviyesi'].strip()) < 1:
        return False, "Kur seviyesi gereklidir"
    
    # Doğum tarihi kontrolü
    if not data.get('dogum_tarihi'):
        return False, "Doğum tarihi gereklidir"
    
    # Cinsiyet kontrolü
    if not data.get('cinsiyet'):
        return False, "Cinsiyet seçimi gereklidir"
    
    # Adres kontrolü
    if not data.get('adres') or len(data['adres'].strip()) < 10:
        return False, "Adres en az 10 karakter olmalıdır"
    
    return True, ""


def sanitize_phone(phone: str) -> str:
    """Telefon numarası temizleme"""
    if not phone:
        return ""
    # Sadece rakam ve + işareti
    cleaned = re.sub(r'[^\d+]', '', phone.strip())
    return cleaned


def sanitize_name(name: str) -> str:
    """İsim temizleme"""
    if not name:
        return ""
    # Sadece harf, boşluk ve Türkçe karakterler
    cleaned = re.sub(r'[^a-zA-ZğüşıöçĞÜŞİÖÇ\s]', '', name.strip())
    return cleaned.title()


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