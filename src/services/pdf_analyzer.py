"""
PDF Dekont Analiz Servisi
Dekontlardan otomatik bilgi çıkarma işlemleri
Gemini AI ile gelişmiş analiz
"""
import re
import os
from datetime import datetime
from typing import Dict, Optional, Any
import pdfplumber
import PyPDF2
from pathlib import Path

# Gemini AI import kontrolü
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from ..core.logger import get_logger
from ..core.config import get_config


class PDFAnalyzer:
    """PDF dekont analiz sınıfı"""
    
    def __init__(self):
        self.logger = get_logger("pdf_analyzer")
        
        # Gemini AI konfigürasyonu
        try:
            # API key'i config'den al
            config = get_config()
            api_key = config.get('gemini_api_key', "AIzaSyD2LkNVz4pus6dBjAF0aPQFcoUX3sR0OUo")
            if api_key and GEMINI_AVAILABLE and genai is not None:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.use_ai = True
                self.logger.info("Gemini AI başarıyla yapılandırıldı")
            else:
                self.use_ai = False
                if not GEMINI_AVAILABLE:
                    self.logger.warning("google-generativeai kütüphanesi yüklü değil, AI analizi devre dışı")
        except Exception as e:
            self.use_ai = False
            self.logger.error(f"Gemini AI yapılandırma hatası: {e}")
        
        # Türk bankaları listesi
        self.banks = [
            'akbank', 'garanti', 'işbank', 'yapıkredi', 'ziraat', 'vakıfbank',
            'halkbank', 'denizbank', 'kuveyttürk', 'qnb', 'ing', 'enpara',
            'papara', 'paycell', 'birebir', 'mobil', 'mobilbank', 'mobilbanking',
            'internet', 'online', 'web', 'app', 'uygulama'
        ]
        
        # Para birimi regex'leri
        self.currency_patterns = [
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*(?:TL|₺|lira|türk\s*lirası)',
            r'(?:TL|₺|lira|türk\s*lirası)\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*(?:USD|dolar)',
            r'(?:USD|dolar)\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*(?:EUR|euro)',
            r'(?:EUR|euro)\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)'
        ]
        
        # Tarih regex'leri
        self.date_patterns = [
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})',  # DD/MM/YYYY
            r'(\d{4})[/\-\.](\d{1,2})[/\-\.](\d{1,2})',  # YYYY/MM/DD
            r'(\d{1,2})\s*(\w+)\s*(\d{4})',  # DD Month YYYY
        ]
        
        # Saat regex'leri
        self.time_patterns = [
            r'(\d{1,2}):(\d{2})(?::(\d{2}))?',  # HH:MM:SS
            r'(\d{1,2})\.(\d{2})',  # HH.MM
        ]
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF'den metin çıkar"""
        try:
            text = ""
            
            # Önce pdfplumber ile dene
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                self.logger.warning(f"pdfplumber ile okuma başarısız: {e}")
                
                # PyPDF2 ile dene
                try:
                    with open(pdf_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page in pdf_reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                except Exception as e2:
                    self.logger.error(f"PyPDF2 ile de okuma başarısız: {e2}")
                    return ""
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"PDF metin çıkarma hatası: {e}")
            return ""
    
    def extract_sender_name(self, text: str) -> Optional[str]:
        """Gönderen kişinin adını çıkar"""
        try:
            # Yaygın gönderen kalıpları
            sender_patterns = [
                r'gönderen[:\s]*([^\n\r]+)',
                r'gönderen\s*kişi[:\s]*([^\n\r]+)',
                r'kimden[:\s]*([^\n\r]+)',
                r'gönderici[:\s]*([^\n\r]+)',
                r'ödeme\s*yapan[:\s]*([^\n\r]+)',
                r'ödeme\s*eden[:\s]*([^\n\r]+)',
                r'kart\s*sahibi[:\s]*([^\n\r]+)',
                r'hesap\s*sahibi[:\s]*([^\n\r]+)',
                r'isim[:\s]*([^\n\r]+)',
                r'ad[:\s]*([^\n\r]+)',
                r'kullanıcı[:\s]*([^\n\r]+)',
                r'müşteri[:\s]*([^\n\r]+)'
            ]
            
            for pattern in sender_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    # Sadece harf ve boşluk içeren isimleri al
                    if re.match(r'^[a-zA-ZğüşıöçĞÜŞİÖÇ\s]+$', name):
                        return name
            
            return None
            
        except Exception as e:
            self.logger.error(f"Gönderen adı çıkarma hatası: {e}")
            return None
    
    def extract_amount(self, text: str) -> Optional[float]:
        """Tutar bilgisini çıkar"""
        try:
            for pattern in self.currency_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    amount_str = match.group(1)
                    # Nokta ve virgülleri düzelt
                    amount_str = amount_str.replace('.', '').replace(',', '.')
                    try:
                        amount = float(amount_str)
                        if amount > 0:
                            return amount
                    except ValueError:
                        continue
            
            # Sadece sayı arama
            number_patterns = [
                r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
                r'(\d+(?:,\d{2})?)',
                r'(\d+(?:\.\d{2})?)'
            ]
            
            for pattern in number_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    try:
                        amount_str = match.replace('.', '').replace(',', '.')
                        amount = float(amount_str)
                        if 1 <= amount <= 100000:  # Makul tutar aralığı
                            return amount
                    except ValueError:
                        continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Tutar çıkarma hatası: {e}")
            return None
    
    def extract_bank_name(self, text: str) -> Optional[str]:
        """Banka adını çıkar"""
        try:
            text_lower = text.lower()
            
            # Banka isimlerini ara
            for bank in self.banks:
                if bank in text_lower:
                    return bank.title()
            
            # Yaygın banka kalıpları
            bank_patterns = [
                r'banka[:\s]*([^\n\r]+)',
                r'bank[:\s]*([^\n\r]+)',
                r'hesap[:\s]*([^\n\r]+)',
                r'kart[:\s]*([^\n\r]+)'
            ]
            
            for pattern in bank_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    bank_name = match.group(1).strip()
                    # Sadece harf ve boşluk içeren banka adlarını al
                    if re.match(r'^[a-zA-ZğüşıöçĞÜŞİÖÇ\s]+$', bank_name):
                        return bank_name
            
            return None
            
        except Exception as e:
            self.logger.error(f"Banka adı çıkarma hatası: {e}")
            return None
    
    def extract_date_time(self, text: str) -> Optional[Dict[str, Any]]:
        """Tarih ve saat bilgisini çıkar"""
        try:
            # Tarih arama
            date_found = None
            for pattern in self.date_patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        if len(match.group(1)) == 4:  # YYYY/MM/DD
                            year, month, day = match.groups()
                        else:  # DD/MM/YYYY
                            day, month, year = match.groups()
                        
                        if len(year) == 2:
                            year = '20' + year
                        
                        date_found = datetime(int(year), int(month), int(day))
                        break
                    except ValueError:
                        continue
            
            # Saat arama
            time_found = None
            for pattern in self.time_patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        hour = int(match.group(1))
                        minute = int(match.group(2))
                        second = int(match.group(3)) if len(match.groups()) > 2 else 0
                        
                        if 0 <= hour <= 23 and 0 <= minute <= 59:
                            time_found = datetime.now().replace(
                                hour=hour, minute=minute, second=second, microsecond=0
                            )
                            break
                    except ValueError:
                        continue
            
            result = {}
            if date_found:
                result['date'] = date_found.strftime('%Y-%m-%d')
            if time_found:
                result['time'] = time_found.strftime('%H:%M:%S')
            
            return result if result else None
            
        except Exception as e:
            self.logger.error(f"Tarih/saat çıkarma hatası: {e}")
            return None
    
    def analyze_with_ai(self, text: str) -> Dict[str, Any]:
        """Gemini AI ile gelişmiş analiz"""
        try:
            if not self.use_ai or not GEMINI_AVAILABLE:
                return {}
            
            prompt = f"""
            Sadece geçerli JSON döndür. Açıklama, başlık, kod bloğu veya başka bir şey ekleme.
            Bu bir Türk bankası dekontu. Aşağıdaki bilgileri JSON formatında çıkar.
            Farklı bankalar farklı anahtar kelimeler kullanabilir, bu yüzden dikkatli analiz et.

            Metin:
            {text}  # Tüm metin

            Çıkarılacak bilgiler:
            - sender_name: Gönderen kişinin adı (Gönderen, Kimden, Kart Sahibi, Hesap Sahibi vb.)
            - amount: Sadece alıcıya ulaşan NET tutar (gönderilen para). İşlem masrafı, komisyon, toplam masraf, ücret, BSMV, mesaj ücreti gibi kalemleri amount olarak DİKKATE ALMA. Sadece alıcıya ulaşan gerçek para miktarını amount olarak döndür.
            - bank_name: Banka adı (Ziraat, Garanti, İşbank, Yapı Kredi vb.)
            - transaction_date: İşlem tarihi (YYYY-MM-DD formatında)
            - transaction_time: İşlem saati (HH:MM formatında)

            Önemli: Farklı bankalar farklı formatlar kullanır:
            - Ziraat: "Gönderen: AD SOYAD"
            - Garanti: "Kart Sahibi: AD SOYAD" 
            - İşbank: "Hesap Sahibi: AD SOYAD"
            - Tutar: "TUTAR: 1.234,56 TL" veya "MİKTAR: 1234.56"
            - Masraf, komisyon, toplam masraf, ücret, BSMV, mesaj ücreti gibi kalemleri asla amount olarak alma.

            Sadece JSON formatında yanıt ver, başka açıklama ekleme.
            Örnek format:
            {{
                "sender_name": "Ad Soyad",
                "amount": 1000.50,
                "bank_name": "Garanti Bankası",
                "transaction_date": "2025-07-06",
                "transaction_time": "15:30"
            }}
            Sadece geçerli JSON döndür.
            """
            
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            import json
            try:
                ai_result = json.loads(response_text)
                self.logger.info(f"AI analizi başarılı: {ai_result}")
                return ai_result
            except json.JSONDecodeError:
                # Yanıttan ilk ve son süslü parantez arasını alıp tekrar dene
                import re
                match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if match:
                    try:
                        ai_result = json.loads(match.group(0))
                        self.logger.info(f"AI analizi (toleranslı) başarılı: {ai_result}")
                        return ai_result
                    except Exception as e2:
                        self.logger.warning(f"AI yanıtı JSON formatında değil (toleranslı deneme başarısız): {e2}")
                self.logger.warning(f"AI yanıtı JSON formatında değil. Yanıt: {response_text}")
                return {}
        except Exception as e:
            self.logger.error(f"AI analizi hatası: {e}")
            return {}
    
    def analyze_dekont(self, pdf_path: str) -> Dict[str, Any]:
        """Dekont analizi yap"""
        try:
            if not os.path.exists(pdf_path):
                self.logger.error(f"PDF dosyası bulunamadı: {pdf_path}")
                return {}
            
            # PDF'den metin çıkar
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                self.logger.warning("PDF'den metin çıkarılamadı")
                return {}
            
            # Önce AI analizi dene
            ai_result = self.analyze_with_ai(text)
            
            # Manuel analiz (fallback)
            sender_name = self.extract_sender_name(text)
            amount = self.extract_amount(text)
            bank_name = self.extract_bank_name(text)
            date_time = self.extract_date_time(text)
            
            # AI sonucu varsa kullan, yoksa manuel sonucu kullan
            result = {
                'sender_name': ai_result.get('sender_name') or sender_name,
                'amount': ai_result.get('amount') or amount,
                'bank_name': ai_result.get('bank_name') or bank_name,
                'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'raw_text': text,  # Tüm metin
                'ai_used': bool(ai_result),
                'confidence_score': 0.9 if ai_result else 0.7  # AI kullanıldıysa daha yüksek güven
            }
            
            # Tarih/saat bilgilerini ekle
            if ai_result.get('transaction_date'):
                result['date'] = ai_result['transaction_date']
            if ai_result.get('transaction_time'):
                result['time'] = ai_result['transaction_time']
            elif date_time:
                result.update(date_time)
            
            self.logger.info(f"Dekont analizi tamamlandı: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Dekont analizi hatası: {e}")
            return {}


def get_pdf_analyzer() -> PDFAnalyzer:
    """PDF analyzer instance'ı döndür"""
    return PDFAnalyzer() 