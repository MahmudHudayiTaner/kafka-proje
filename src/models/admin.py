"""
Admin modeli
"""
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib
import os

class Admin:
    """Admin kullanıcı modeli"""
    
    def __init__(self, 
                 username: str,
                 password_hash: str,
                 is_active: bool = True,
                 created_at: Optional[datetime] = None):
        
        self.username = username
        self.password_hash = password_hash
        self.is_active = is_active
        self.created_at = created_at or datetime.now()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Şifreyi hash'le"""
        salt = os.urandom(32)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + hash_obj.hex()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Şifreyi doğrula"""
        try:
            # Salt'ı ayır (ilk 64 karakter)
            salt_hex = password_hash[:64]
            hash_hex = password_hash[64:]
            
            salt = bytes.fromhex(salt_hex)
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            
            return hash_obj.hex() == hash_hex
        except:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary formatına çevir"""
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'is_active': self.is_active,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Admin':
        """Dictionary'den Admin oluştur"""
        return cls(
            username=data.get('username', ''),
            password_hash=data.get('password_hash', ''),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at')
        )
    
    def __str__(self) -> str:
        return f"Admin({self.username})"
    
    def __repr__(self) -> str:
        return self.__str__() 