import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from flask import session
from web.app import app as flask_app
from src.core.database import get_database
from src.services.pdf_analyzer import get_pdf_analyzer

def unique_email():
    import uuid
    return f"test_all_{uuid.uuid4()}@example.com"

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client

def test_admin_login_logout(client):
    # Admin login
    response = client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert 'Hoş geldiniz'.encode('utf-8') in response.data or b'Dashboard' in response.data
    # Admin logout
    response = client.get('/admin/logout', follow_redirects=True)
    assert 'Başarıyla çıkış yaptınız'.encode('utf-8') in response.data

def test_user_basvuru_and_pdf_analysis(client):
    # PDF ile başvuru
    data = {
        'ad': 'TestAll',
        'soyad': 'Kullanıcı',
        'telefon': '05551231212',
        'eposta': unique_email(),
        'dogum_tarihi': '2000-01-01',
        'cinsiyet': 'Kadın',
        'adres': 'Test Mah. Test Cad. No:1',
        'kur_seviyesi': 'A1',
    }
    pdf_path = os.path.join('tests', 'dekontlar', 'test_dekont2.pdf')
    with open(pdf_path, 'rb') as f:
        data_with_file = dict(data)
        data_with_file['pdf_dosya'] = (f, 'test_dekont2.pdf')
        response = client.post('/submit', data=data_with_file, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert 'Başvurunuz başarıyla kaydedildi'.encode('utf-8') in response.data
    # Veritabanında başvuru ve analiz kontrolü
    db = get_database()
    basvurular = db.basvurulari_listele(limit=1)
    assert basvurular, 'Başvuru veritabanında yok!'
    basvuru = basvurular[0]
    if basvuru['pdf_dosya_yolu']:
        import time
        time.sleep(2)  # Arka plan analiz için kısa bekle
        analiz = db.basvuru_dekont_analizi_getir(basvuru['id'])
        assert analiz is not None, 'Dekont analizi yapılmadı!'
        assert 'amount' in analiz

def test_admin_basvurular_listesi(client):
    # Admin login
    client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    response = client.get('/admin/basvurular')
    assert 'Başvurular'.encode('utf-8') in response.data or 'Başvuru'.encode('utf-8') in response.data

def test_pdf_analyzer_module():
    analyzer = get_pdf_analyzer()
    pdf_path = os.path.join('tests', 'dekontlar', 'test_dekont2.pdf')
    result = analyzer.analyze_dekont(pdf_path)
    assert isinstance(result, dict)
    assert 'amount' in result
    assert 'sender_name' in result
    assert 'bank_name' in result
    assert 'raw_text' in result
    print('[RAPOR] PDF analiz modülü çalışıyor.') 