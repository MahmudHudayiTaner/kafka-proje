"""
Konfigürasyon yönetimi
"""
import os
import pandas as pd
from typing import Dict, Any
from pathlib import Path


class Config:
    """Uygulama konfigürasyonu yönetimi"""
    
    def __init__(self, config_path: str = "config.xlsx"):
        self.config_path = config_path
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Excel dosyasından konfigürasyon yükle"""
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Konfigürasyon dosyası bulunamadı: {self.config_path}")
            
            df = pd.read_excel(self.config_path, engine='openpyxl')
            config_dict = dict(zip(df['Name'], df['Value']))
            
            # Gerekli alanları kontrol et
            required_fields = ['mail', 'mail_app_password', 'imap_server', 'db']
            missing_fields = [field for field in required_fields if field not in config_dict]
            
            if missing_fields:
                raise ValueError(f"Eksik konfigürasyon alanları: {missing_fields}")
                
            return config_dict
            
        except Exception as e:
            raise RuntimeError(f"Konfigürasyon yüklenirken hata: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Konfigürasyon değeri al"""
        return self._config.get(key, default)
    
    def get_email_config(self) -> Dict[str, str]:
        """Email konfigürasyonu al"""
        return {
            'email': self.get('mail'),
            'password': self.get('mail_app_password'),
            'imap_server': self.get('imap_server')
        }
    
    def get_database_path(self) -> str:
        """Veritabanı yolu al"""
        return self.get('db', 'db_kafka.db')
    
    def get_gemini_api_key(self) -> str:
        """Gemini API anahtarı al"""
        return self.get('gemini_api_key', '')
    
    def get_log_level(self) -> str:
        """Log seviyesi al"""
        return self.get('log_level', 'INFO')
    
    def get_log_path(self) -> str:
        """Log dosyası yolu al"""
        return self.get('log_path', 'logs/app.log')
    
    def validate(self) -> bool:
        """Konfigürasyon geçerliliğini kontrol et"""
        try:
            # Email ayarları kontrolü
            email_config = self.get_email_config()
            if not all(email_config.values()):
                raise ValueError("Email konfigürasyonu eksik")
            
            # Veritabanı yolu kontrolü
            db_path = self.get_database_path()
            if not db_path:
                raise ValueError("Veritabanı yolu belirtilmemiş")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Konfigürasyon geçersiz: {e}")


# Singleton instance
_config_instance = None

def get_config() -> Config:
    """Konfigürasyon instance'ı al"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance 