"""
Basit Başvuru Formu - Web Uygulaması
"""
import os
import sys
from datetime import datetime, date
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

# src klasörünü Python path'ine ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.database import get_database
from src.core.logger import get_logger
from src.models.basvuru import Basvuru
from src.models.admin import Admin
from src.utils.validators import validate_basvuru_data, sanitize_name, sanitize_phone

app = Flask(__name__)
app.secret_key = 'kafka_proje_secret_key_2024'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 saat

# Konfigürasyon
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Servisler
db = get_database()
logger = get_logger("web_app")

def allowed_file(filename):
    """Dosya uzantısı kontrolü"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hesapla_yas(dogum_tarihi_str):
    """Doğum tarihinden yaş hesapla"""
    if not dogum_tarihi_str:
        return None
    
    try:
        dogum_tarihi = datetime.strptime(dogum_tarihi_str, '%Y-%m-%d').date()
        bugun = date.today()
        yas = bugun.year - dogum_tarihi.year
        
        # Doğum günü henüz gelmediyse yaşı bir azalt
        if (bugun.month, bugun.day) < (dogum_tarihi.month, dogum_tarihi.day):
            yas -= 1
            
        return yas
    except:
        return None

def format_tarih(tarih_str):
    """Tarihi gün.ay.yıl 00:00 formatında formatla"""
    if not tarih_str:
        return '-'
    
    try:
        # Tarih ve saat ayrımı
        if ' ' in tarih_str:
            tarih_part, saat_part = tarih_str.split(' ', 1)
        else:
            tarih_part = tarih_str
            saat_part = '00:00:00'
        
        # Sadece saat ve dakika al (saniyeyi kaldır)
        saat_kisa = ':'.join(saat_part.split(':')[:2])
        
        # Tarih formatını değiştir
        tarih_obj = datetime.strptime(tarih_part, '%Y-%m-%d')
        return f"{tarih_obj.day:02d}.{tarih_obj.month:02d}.{tarih_obj.year} {saat_kisa}"
    except:
        return tarih_str

def login_required(f):
    """Login gerektiren sayfalar için decorator"""
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Bu sayfaya erişmek için giriş yapmalısınız!', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    """Ana sayfa - Başvuru formu"""
    # Session kontrolü - eğer admin girişi varsa dashboard'a yönlendir
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_basvuru():
    """Başvuru formu gönderimi"""
    try:
        # Form verilerini al
        basvuru_data = {
            'ad': request.form.get('ad', '').strip(),
            'soyad': request.form.get('soyad', '').strip(),
            'telefon': request.form.get('telefon', '').strip(),
            'eposta': request.form.get('eposta', '').strip(),
            'dogum_tarihi': request.form.get('dogum_tarihi', ''),
            'cinsiyet': request.form.get('cinsiyet', ''),
            'adres': request.form.get('adres', '').strip(),
            'kur_seviyesi': request.form.get('kur_seviyesi', '').strip(),
            'basvuru_tarihi': datetime.now(),
            'pdf_dosya_yolu': None,
            'pdf_icerik': None,
            'ai_analiz_sonucu': None
        }
        
        # Verileri temizle
        basvuru_data['ad'] = sanitize_name(basvuru_data['ad'])
        basvuru_data['soyad'] = sanitize_name(basvuru_data['soyad'])
        basvuru_data['telefon'] = sanitize_phone(basvuru_data['telefon'])
        
        # PDF dosyası kontrolü (opsiyonel)
        if 'pdf_dosya' in request.files:
            file = request.files['pdf_dosya']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    # Güvenli dosya adı oluştur
                    original_filename = file.filename or 'unknown.pdf'
                    filename = secure_filename(original_filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    
                    # Upload klasörünü oluştur
                    upload_path = Path(app.config['UPLOAD_FOLDER'])
                    upload_path.mkdir(exist_ok=True)
                    
                    # Dosyayı kaydet
                    file_path = upload_path / filename
                    file.save(str(file_path))
                    
                    basvuru_data['pdf_dosya_yolu'] = str(file_path)
                    logger.info(f"PDF dosyası yüklendi: {filename}")
                else:
                    flash('Sadece PDF, PNG, JPG ve JPEG dosyaları kabul edilir!', 'error')
                    return redirect(url_for('index'))
        
        # Tarih zaten datetime.now() olarak ayarlandı
        
        # Veri doğrulama
        is_valid, error = validate_basvuru_data(basvuru_data)
        if not is_valid:
            flash(f'Form hatası: {error}', 'error')
            return redirect(url_for('index'))
        
        # Başvuru modeli oluştur
        basvuru = Basvuru(
            ad=basvuru_data['ad'],
            soyad=basvuru_data['soyad'],
            telefon=basvuru_data['telefon'],
            eposta=basvuru_data['eposta'],
            dogum_tarihi=basvuru_data['dogum_tarihi'],
            cinsiyet=basvuru_data['cinsiyet'],
            adres=basvuru_data['adres'],
            kur_seviyesi=basvuru_data['kur_seviyesi'],
            basvuru_tarihi=basvuru_data['basvuru_tarihi'],
            pdf_dosya_yolu=basvuru_data['pdf_dosya_yolu'],
            pdf_icerik=basvuru_data['pdf_icerik'],
            ai_analiz_sonucu=basvuru_data['ai_analiz_sonucu']
        )
        
        # Veritabanına kaydet
        basvuru_id = db.basvuru_ekle(basvuru.to_dict())
        
        if basvuru_id:
            flash(f'Başvurunuz başarıyla kaydedildi!', 'success')
            logger.info(f"Yeni başvuru kaydedildi: ID={basvuru_id}, Ad={basvuru.tam_ad()}")
        else:
            if basvuru_data.get('eposta'):
                flash('Bu email adresi ile daha önce başvuru yapılmış! Her email adresi ile sadece bir kez başvuru yapılabilir.', 'error')
            else:
                flash('Başvuru kaydedilirken bir hata oluştu!', 'error')
            logger.error("Başvuru kaydedilemedi")
        
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Başvuru gönderimi hatası: {e}")
        flash('Beklenmeyen bir hata oluştu!', 'error')
        return redirect(url_for('index'))

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin giriş sayfası"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Kullanıcı adı ve şifre gereklidir!', 'error')
            return render_template('admin_login.html')
        
        # Şifre doğrulama
        if db.admin_verify_password(username, password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash(f'Hoş geldiniz, {username}!', 'success')
            logger.info(f"Admin giriş yaptı: {username}")
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre!', 'error')
            logger.warning(f"Başarısız admin giriş denemesi: {username}")
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin çıkış"""
    session.clear()  # Tüm session'ı temizle
    flash('Başarıyla çıkış yaptınız!', 'success')
    logger.info("Admin çıkış yaptı")
    return redirect(url_for('index'))

@app.route('/clear-session')
def clear_session():
    """Session'ı temizle (test için)"""
    session.clear()
    flash('Session temizlendi!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin paneli"""
    try:
        # İstatistikleri hesapla
        basvurular = db.basvurulari_listele(limit=1000)
        ogrenciler = db.ogrencileri_listele(limit=1000)
        odemeler = db.odemeleri_listele(limit=1000)
        
        stats = {
            'toplam_basvuru': len(basvurular),
            'bekleyen_basvuru': len([b for b in basvurular if b['durum'] == 'beklemede']),
            'onaylanan_basvuru': len([b for b in basvurular if b['durum'] == 'onaylandi']),
            'toplam_ogrenci': len(ogrenciler),
            'aktif_ogrenci': len([o for o in ogrenciler if o['durum'] == 'aktif']),
            'toplam_odeme': len(odemeler),
            'bekleyen_odeme': len([o for o in odemeler if o['durum'] == 'beklemede'])
        }
        
        return render_template('admin_dashboard.html', stats=stats)
        
    except Exception as e:
        logger.error(f"Admin dashboard hatası: {e}")
        flash('Dashboard yüklenirken bir hata oluştu.', 'error')
        return render_template('admin_dashboard.html', stats={})

@app.route('/admin/basvurular')
@login_required
def admin_basvurular():
    """Admin başvuru listesi"""
    try:
        basvurular = db.basvurulari_listele(limit=50)
        
        # Her başvuru için yaş hesapla ve tarih formatla
        for basvuru in basvurular:
            basvuru['yas'] = hesapla_yas(basvuru.get('dogum_tarihi'))
            basvuru['basvuru_tarihi_formatted'] = format_tarih(basvuru.get('basvuru_tarihi'))
        
        return render_template('admin_basvurular.html', basvurular=basvurular)
    except Exception as e:
        logger.error(f"Admin başvuru listesi hatası: {e}")
        flash('Başvurular yüklenirken hata oluştu!', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/basvuru/<int:basvuru_id>')
@login_required
def admin_basvuru_detay(basvuru_id):
    """Başvuru detayı"""
    try:
        basvuru = db.basvuru_getir(basvuru_id)
        if basvuru:
            # Yaş hesapla ve tarih formatla
            basvuru['yas'] = hesapla_yas(basvuru.get('dogum_tarihi'))
            basvuru['basvuru_tarihi_formatted'] = format_tarih(basvuru.get('basvuru_tarihi'))
            return render_template('admin_basvuru_detay.html', basvuru=basvuru)
        else:
            flash('Başvuru bulunamadı!', 'error')
            return redirect(url_for('admin_basvurular'))
    except Exception as e:
        logger.error(f"Başvuru detay hatası: {e}")
        flash('Başvuru detayı yüklenirken hata oluştu!', 'error')
        return redirect(url_for('admin_basvurular'))

@app.route('/admin/basvuru/<int:basvuru_id>/delete', methods=['POST'])
@login_required
def admin_basvuru_sil(basvuru_id):
    """Başvuru sil"""
    try:
        if db.basvuru_sil(basvuru_id):
            flash('Başvuru başarıyla silindi!', 'success')
        else:
            flash('Başvuru silinirken hata oluştu!', 'error')
    except Exception as e:
        logger.error(f"Başvuru silme hatası: {e}")
        flash('Başvuru silinirken hata oluştu!', 'error')
    
    return redirect(url_for('admin_basvurular'))

@app.route('/admin/basvuru/<int:basvuru_id>/convert-to-student', methods=['POST'])
@login_required
def admin_basvuru_ogrenciye_cevir(basvuru_id):
    """Başvuruyu öğrenciye çevir"""
    try:
        # Başvuruyu getir
        basvuru = db.basvuru_getir(basvuru_id)
        if not basvuru:
            flash('Başvuru bulunamadı!', 'error')
            return redirect(url_for('admin_basvurular'))
        
        # Öğrenci verisi oluştur
        ogrenci_data = {
            'ad': basvuru['ad'],
            'soyad': basvuru['soyad'],
            'telefon': basvuru['telefon'],
            'eposta': basvuru['eposta'],
            'aktif_seviye': basvuru['kur_seviyesi'],
            'toplam_seviye_sayisi': 1,
            'durum': 'aktif'
        }
        
        # Öğrenciyi ekle
        ogrenci_id = db.ogrenci_ekle(ogrenci_data)
        
        if ogrenci_id:
            # İlk seviye kaydını oluştur
            seviye_data = {
                'ogrenci_id': ogrenci_id,
                'seviye': basvuru['kur_seviyesi'],
                'baslama_tarihi': datetime.now(),
                'ucret': 0,  # Varsayılan ücret
                'kalan_miktar': 0
            }
            
            db.seviye_kaydi_ekle(seviye_data)
            
            # Başvuruyu sil (opsiyonel - isterseniz silmeyebilirsiniz)
            # db.basvuru_sil(basvuru_id)
            
            flash(f'Başvuru başarıyla öğrenciye çevrildi! Öğrenci ID: {ogrenci_id}', 'success')
            logger.info(f"Başvuru öğrenciye çevrildi: Başvuru ID={basvuru_id}, Öğrenci ID={ogrenci_id}")
        else:
            flash('Öğrenci kaydı oluşturulurken hata oluştu!', 'error')
            
    except Exception as e:
        logger.error(f"Başvuru öğrenciye çevirme hatası: {e}")
        flash('Başvuru öğrenciye çevrilirken hata oluştu!', 'error')
    
    return redirect(url_for('admin_basvurular'))

@app.route('/admin/basvurular/bulk-delete', methods=['POST'])
@login_required
def admin_basvuru_toplu_sil():
    """Toplu başvuru sil"""
    try:
        selected_ids = request.form.get('selected_ids', '').split(',')
        selected_ids = [int(id.strip()) for id in selected_ids if id.strip().isdigit()]
        
        if not selected_ids:
            flash('Silinecek başvuru seçilmedi!', 'error')
            return redirect(url_for('admin_basvurular'))
        
        success_count = 0
        for basvuru_id in selected_ids:
            if db.basvuru_sil(basvuru_id):
                success_count += 1
        
        if success_count > 0:
            flash(f'{success_count} başvuru başarıyla silindi!', 'success')
        else:
            flash('Başvurular silinirken hata oluştu!', 'error')
            
    except Exception as e:
        logger.error(f"Toplu başvuru silme hatası: {e}")
        flash('Başvurular silinirken hata oluştu!', 'error')
    
    return redirect(url_for('admin_basvurular'))

# Öğrenci yönetimi rotaları
@app.route('/admin/ogrenciler')
def admin_ogrenciler():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        ogrenciler = db.ogrencileri_listele()
        return render_template('admin_ogrenciler.html', ogrenciler=ogrenciler)
    except Exception as e:
        logger.error(f"Admin öğrenci listeleme hatası: {e}")
        flash('Öğrenciler yüklenirken bir hata oluştu.', 'error')
        return render_template('admin_ogrenciler.html', ogrenciler=[])

@app.route('/admin/ogrenci/<int:ogrenci_id>')
def admin_ogrenci_detay(ogrenci_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        ogrenci = db.ogrenci_getir(ogrenci_id)
        
        if not ogrenci:
            flash('Öğrenci bulunamadı!', 'error')
            return redirect(url_for('admin_ogrenciler'))
        
        # Öğrencinin seviyelerini getir
        seviyeler = db.ogrenci_seviyeleri_getir(ogrenci_id)
        
        # Öğrencinin ödemelerini getir
        odemeler = db.odemeleri_listele(ogrenci_id=ogrenci_id)
        
        return render_template('admin_ogrenci_detay.html', 
                             ogrenci=ogrenci, 
                             seviyeler=seviyeler, 
                             odemeler=odemeler)
        
    except Exception as e:
        logger.error(f"Admin öğrenci detay hatası: {e}")
        flash('Öğrenci detayı yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('admin_ogrenciler'))

@app.route('/admin/ogrenci/<int:ogrenci_id>/seviye-ekle', methods=['POST'])
def admin_seviye_ekle(ogrenci_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        seviye = request.form['seviye']
        ucret = float(request.form['ucret'])
        
        seviye_data = {
            'ogrenci_id': ogrenci_id,
            'seviye': seviye,
            'baslama_tarihi': datetime.now(),
            'ucret': ucret,
            'kalan_miktar': ucret
        }
        
        seviye_id = db.seviye_kaydi_ekle(seviye_data)
        
        if seviye_id:
            flash(f'Yeni seviye başarıyla eklendi: {seviye}', 'success')
        else:
            flash('Seviye eklenirken bir hata oluştu.', 'error')
            
    except Exception as e:
        logger.error(f"Seviye ekleme hatası: {e}")
        flash('Seviye eklenirken bir hata oluştu.', 'error')
    
    return redirect(url_for('admin_ogrenci_detay', ogrenci_id=ogrenci_id))

@app.route('/admin/odeme-ekle', methods=['POST'])
def admin_odeme_ekle():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        ogrenci_id = int(request.form['ogrenci_id'])
        seviye_id = int(request.form['seviye_id'])
        odeme_tipi = request.form['odeme_tipi']
        miktar = float(request.form['miktar'])
        aciklama = request.form.get('aciklama', '')
        
        # Dekont dosyasını kontrol et
        dekont_yolu = None
        if 'dekont' in request.files:
            file = request.files['dekont']
            if file and file.filename and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                dekont_yolu = filename
        
        odeme_data = {
            'ogrenci_id': ogrenci_id,
            'seviye_id': seviye_id,
            'odeme_tipi': odeme_tipi,
            'miktar': miktar,
            'dekont_yolu': dekont_yolu,
            'aciklama': aciklama
        }
        
        odeme_id = db.odeme_ekle(odeme_data)
        
        if odeme_id:
            flash('Ödeme başarıyla eklendi!', 'success')
        else:
            flash('Ödeme eklenirken bir hata oluştu.', 'error')
            
    except Exception as e:
        logger.error(f"Ödeme ekleme hatası: {e}")
        flash('Ödeme eklenirken bir hata oluştu.', 'error')
    
    return redirect(url_for('admin_ogrenci_detay', ogrenci_id=ogrenci_id))

@app.route('/admin/odeme/<int:odeme_id>/onayla', methods=['POST'])
def admin_odeme_onayla(odeme_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        if db.odeme_onayla(odeme_id):
            flash('Ödeme başarıyla onaylandı!', 'success')
        else:
            flash('Ödeme onaylanırken bir hata oluştu.', 'error')
            
    except Exception as e:
        logger.error(f"Ödeme onaylama hatası: {e}")
        flash('Ödeme onaylanırken bir hata oluştu.', 'error')
    
    return redirect(request.referrer or url_for('admin_ogrenciler'))

@app.route('/admin/odemeler')
def admin_odemeler():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        odemeler = db.odemeleri_listele()
        return render_template('admin_odemeler.html', odemeler=odemeler)
    except Exception as e:
        logger.error(f"Admin ödeme listeleme hatası: {e}")
        flash('Ödemeler yüklenirken bir hata oluştu.', 'error')
        return render_template('admin_odemeler.html', odemeler=[])

if __name__ == '__main__':
    import os
    from production_config import PRODUCTION_CONFIG
    
    # Production ayarlarını yükle
    if os.environ.get('FLASK_ENV') == 'production':
        app.config.update(PRODUCTION_CONFIG)
        app.run(
            host=PRODUCTION_CONFIG['HOST'],
            port=int(os.environ.get('PORT', PRODUCTION_CONFIG['PORT'])),
            debug=False
        )
    else:
        # Development modu
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        ) 