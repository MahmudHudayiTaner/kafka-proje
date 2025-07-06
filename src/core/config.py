"""
Basit konfigürasyon yönetimi
"""
import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """Uygulama konfigürasyonu yönetimi"""
    
    def __init__(self):
        self._config = self._load_default_config()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Varsayılan konfigürasyon yükle"""
        return {
            'database_path': 'data/basvurular.db',
            'log_level': 'INFO',
            'log_path': 'logs/app.log',
            'upload_folder': 'web/uploads',
            'max_file_size': 16 * 1024 * 1024,  # 16MB
            'allowed_extensions': ['pdf']
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Konfigürasyon değeri al"""
        return self._config.get(key, default)
    
    def get_database_path(self) -> str:
        """Veritabanı yolu al"""
        return self.get('database_path', 'data/basvurular.db')
    
    def get_log_level(self) -> str:
        """Log seviyesi al"""
        return self.get('log_level', 'INFO')
    
    def get_log_path(self) -> str:
        """Log dosyası yolu al"""
        return self.get('log_path', 'logs/app.log')
    
    def get_upload_folder(self) -> str:
        """Upload klasörü yolu al"""
        return self.get('upload_folder', 'web/uploads')
    
    def get_max_file_size(self) -> int:
        """Maksimum dosya boyutu al"""
        return self.get('max_file_size', 16 * 1024 * 1024)
    
    def get_allowed_extensions(self) -> list:
        """İzin verilen dosya uzantıları al"""
        return self.get('allowed_extensions', ['pdf'])


# Singleton instance
_config_instance = None

def get_config() -> Config:
    """Konfigürasyon instance'ı al"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance 