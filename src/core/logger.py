"""
Profesyonel loglama sistemi
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from .config import get_config


class Logger:
    """Uygulama loglama sistemi"""
    
    def __init__(self, name: str = "kafka_proje"):
        self.name = name
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Logger kurulumu"""
        config = get_config()
        
        # Logger oluştur
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, config.get_log_level()))
        
        # Eğer handler'lar zaten varsa, tekrar ekleme
        if logger.handlers:
            return logger
        
        # Format belirle
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_path = config.get_log_path()
        log_dir = Path(log_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def info(self, message: str) -> None:
        """Info seviyesinde log"""
        self.logger.info(message)
    
    def debug(self, message: str) -> None:
        """Debug seviyesinde log"""
        self.logger.debug(message)
    
    def warning(self, message: str) -> None:
        """Warning seviyesinde log"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Error seviyesinde log"""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Critical seviyesinde log"""
        self.logger.critical(message)
    
    def exception(self, message: str) -> None:
        """Exception log (error + traceback)"""
        self.logger.exception(message)


# Singleton instance
_logger_instance = None

def get_logger(name: str = "kafka_proje") -> Logger:
    """Logger instance'ı al"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger(name)
    return _logger_instance 