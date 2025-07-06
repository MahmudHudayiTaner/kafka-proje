"""
Profesyonel loglama sistemi
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from .config import get_config
from colorama import init, Fore, Style

# Colorama'yı başlat
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Renkli log formatı"""
    
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    def format(self, record):
        # Renk ekle
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        
        # Mesajı renklendir
        if record.levelno >= logging.ERROR:
            record.msg = f"{Fore.RED}{record.msg}{Style.RESET_ALL}"
        elif record.levelno >= logging.WARNING:
            record.msg = f"{Fore.YELLOW}{record.msg}{Style.RESET_ALL}"
        
        return super().format(record)

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
        
        # Eğer handler'lar zaten eklenmişse, tekrar ekleme
        if logger.handlers:
            return logger
        
        # Log seviyesini ayarla
        log_level = getattr(logging, config.get_log_level().upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Log klasörünü oluştur
        log_path = Path(config.get_log_path())
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Dosya handler'ı
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Konsol handler'ı (renkli)
        console_handler = logging.StreamHandler()
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # Handler'ları ekle
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
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