#!/usr/bin/env python3
"""
AI Analiz Test Script'i
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.services.pdf_analyzer import get_pdf_analyzer

def test_ai_analysis():
    """AI analizini test et"""
    print("🤖 AI Analiz Testi Başlatılıyor...")
    print("=" * 50)
    
    # PDF analyzer'ı al
    analyzer = get_pdf_analyzer()
    
    # Test PDF dosyası
    pdf_path = "uploads/20250705_213948_Dekont.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF dosyası bulunamadı: {pdf_path}")
        return
    
    print(f"📄 PDF dosyası: {pdf_path}")
    print(f"🤖 AI kullanımı: {analyzer.use_ai}")
    
    try:
        # PDF analizi yap
        print("\n🔍 PDF analizi yapılıyor...")
        result = analyzer.analyze_dekont(pdf_path)
        
        if result:
            print("✅ Analiz başarılı!")
            print("\n📊 Analiz Sonuçları:")
            print(f"   Gönderen: {result.get('sender_name', 'Bulunamadı')}")
            print(f"   Tutar: {result.get('amount', 'Bulunamadı')}")
            print(f"   Banka: {result.get('bank_name', 'Bulunamadı')}")
            print(f"   Tarih: {result.get('date', 'Bulunamadı')}")
            print(f"   Saat: {result.get('time', 'Bulunamadı')}")
            print(f"   AI Kullanıldı: {result.get('ai_used', False)}")
            print(f"   Güven Skoru: {result.get('confidence_score', 0)}")
        else:
            print("❌ Analiz sonucu boş")
            
    except Exception as e:
        print(f"❌ Analiz hatası: {e}")

if __name__ == "__main__":
    test_ai_analysis() 