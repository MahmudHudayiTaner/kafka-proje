import sys
import os
import uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flask import session
from web.app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client

def unique_email():
    return f"test_{uuid.uuid4()}@example.com"

def test_user_basvuru_success(client):
    """Başarılı başvuru senaryosu (pdf olmadan)"""
    data = {
        'ad': 'Test',
        'soyad': 'Kullanıcı',
        'telefon': '05551231212',
        'eposta': unique_email(),
        'dogum_tarihi': '2000-01-01',
        'cinsiyet': 'Kadın',
        'adres': 'Test Mah. Test Cad. No:1',
        'kur_seviyesi': 'A1',
    }
    response = client.post('/submit', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert 'Başvurunuz başarıyla kaydedildi' in response.data.decode('utf-8')
    print("[RAPOR] Başarılı başvuru (pdf olmadan) geçti.")

def test_user_basvuru_duplicate_email(client):
    """Aynı e-posta ile ikinci başvuru engellenmeli"""
    email = unique_email()
    data1 = {
        'ad': 'Test3',
        'soyad': 'Kullanıcı3',
        'telefon': '05551231214',
        'eposta': email,
        'dogum_tarihi': '2002-03-03',
        'cinsiyet': 'Kadın',
        'adres': 'Test Mah. Test Cad. No:3',
        'kur_seviyesi': 'B1',
    }
    data2 = dict(data1)
    response1 = client.post('/submit', data=data1, content_type='multipart/form-data', follow_redirects=True)
    response2 = client.post('/submit', data=data2, content_type='multipart/form-data', follow_redirects=True)
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert 'Başvurunuz başarıyla kaydedildi' in response1.data.decode('utf-8')
    assert 'Bu email adresi ile daha önce başvuru yapılmış' in response2.data.decode('utf-8')
    print("[RAPOR] Aynı e-posta ile ikinci başvuru engellendi.")

def test_user_basvuru_invalid_data(client):
    """Eksik zorunlu alan ile başvuru reddedilmeli"""
    data = {
        'ad': '',  # zorunlu alan boş
        'soyad': 'Kullanıcı4',
        'telefon': '05551231215',
        'eposta': unique_email(),
        'dogum_tarihi': '2003-04-04',
        'cinsiyet': 'Erkek',
        'adres': 'Test Mah. Test Cad. No:4',
        'kur_seviyesi': 'B2',
    }
    response = client.post('/submit', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert 'Form hatası' in response.data.decode('utf-8')
    print("[RAPOR] Eksik zorunlu alan ile başvuru reddedildi.")

def test_user_basvuru_with_test_dekont2(client):
    data = {
        'ad': 'Dekont2',
        'soyad': 'Test',
        'telefon': '05551111111',
        'eposta': unique_email(),
        'dogum_tarihi': '1991-01-01',
        'cinsiyet': 'Kadın',
        'adres': 'Test Adres 2',
        'kur_seviyesi': 'A2',
    }
    pdf_path = os.path.join('tests', 'dekontlar', 'test_dekont2.pdf')
    with open(pdf_path, 'rb') as f:
        data_with_file = dict(data)
        data_with_file['pdf_dosya'] = (f, 'test_dekont2.pdf')
        response = client.post('/submit', data=data_with_file, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert 'Başvurunuz başarıyla kaydedildi' in response.data.decode('utf-8')
    print("[RAPOR] test_dekont2.pdf ile başvuru başarılı.")

def test_user_basvuru_with_test_dekont3(client):
    data = {
        'ad': 'Dekont3',
        'soyad': 'Test',
        'telefon': '05552222222',
        'eposta': unique_email(),
        'dogum_tarihi': '1992-02-02',
        'cinsiyet': 'Erkek',
        'adres': 'Test Adres 3',
        'kur_seviyesi': 'B1',
    }
    pdf_path = os.path.join('tests', 'dekontlar', 'test_dekont3.pdf')
    with open(pdf_path, 'rb') as f:
        data_with_file = dict(data)
        data_with_file['pdf_dosya'] = (f, 'test_dekont3.pdf')
        response = client.post('/submit', data=data_with_file, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert 'Başvurunuz başarıyla kaydedildi' in response.data.decode('utf-8')
    print("[RAPOR] test_dekont3.pdf ile başvuru başarılı.")

def test_user_basvuru_with_test_dekont4(client):
    data = {
        'ad': 'Dekont4',
        'soyad': 'Test',
        'telefon': '05553333333',
        'eposta': unique_email(),
        'dogum_tarihi': '1993-03-03',
        'cinsiyet': 'Kadın',
        'adres': 'Test Adres 4',
        'kur_seviyesi': 'B2',
    }
    pdf_path = os.path.join('tests', 'dekontlar', 'test_dekont4.pdf')
    with open(pdf_path, 'rb') as f:
        data_with_file = dict(data)
        data_with_file['pdf_dosya'] = (f, 'test_dekont4.pdf')
        response = client.post('/submit', data=data_with_file, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert 'Başvurunuz başarıyla kaydedildi' in response.data.decode('utf-8')
    print("[RAPOR] test_dekont4.pdf ile başvuru başarılı.") 