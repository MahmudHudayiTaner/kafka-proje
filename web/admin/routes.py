from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from datetime import datetime, date
from pathlib import Path
from werkzeug.utils import secure_filename
from src.core.database import get_database
from src.core.logger import get_logger
from src.models.basvuru import Basvuru
from src.models.admin import Admin
from src.utils.validators import validate_basvuru_data, sanitize_name, sanitize_phone
import time

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

db = get_database()
logger = get_logger("admin")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def hesapla_yas(dogum_tarihi):
    if not dogum_tarihi:
        return None
    try:
        if isinstance(dogum_tarihi, str):
            dogum_tarihi = datetime.strptime(dogum_tarihi, '%Y-%m-%d')
        today = datetime.today()
        return today.year - dogum_tarihi.year - ((today.month, today.day) < (dogum_tarihi.month, dogum_tarihi.day))
    except Exception:
        return None

def format_tarih(tarih):
    from datetime import datetime
    if not tarih:
        return ''
    if isinstance(tarih, str):
        try:
            tarih = datetime.strptime(tarih, '%Y-%m-%d')
        except Exception:
            return tarih
    return tarih.strftime('%d.%m.%Y')

@admin_bp.before_request
def check_admin_login():
    # Giriş sayfası ve statik dosyalar hariç kontrol
    allowed_routes = ['admin.admin_login', 'admin.static']
    if request.endpoint in allowed_routes:
        return
    # Oturum kontrolü
    if not session.get('admin_logged_in'):
        flash('Bu sayfaya erişmek için giriş yapmalısınız!', 'error')
        return redirect(url_for('admin.admin_login'))
    # Timeout kontrolü (30 dakika)
    now = time.time()
    last_activity = session.get('last_activity')
    if last_activity and now - last_activity > 1800:
        session.clear()
        flash('Oturum süreniz doldu, lütfen tekrar giriş yapın.', 'warning')
        return redirect(url_for('admin.admin_login'))
    session['last_activity'] = now

@admin_bp.route('/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Bu sayfaya erişmek için giriş yapmalısınız!', 'error')
        return redirect(url_for('admin.admin_login'))
    try:
        # Doğrudan SQL ile toplam başvuru sayısını çek
        import sqlite3
        from src.core.config import get_config
        db_path = get_config().get_database_path()
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM basvurular')
            toplam_basvuru = cursor.fetchone()[0]
        stats = {
            'toplam_basvuru': toplam_basvuru
        }
    except Exception as e:
        stats = {'toplam_basvuru': 0}
    return render_template('admin_dashboard.html', stats=stats)

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Kullanıcı adı ve şifre gereklidir!', 'error')
            return render_template('admin_login.html')
        if db.admin_verify_password(username, password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['last_activity'] = time.time()
            flash(f'Hoş geldiniz, {username}!', 'success')
            logger.info(f"Admin giriş yaptı: {username}")
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre!', 'error')
            logger.warning(f"Başarısız admin giriş denemesi: {username}")
    return render_template('admin_login.html')

@admin_bp.route('/logout')
def admin_logout():
    session.clear()
    flash('Başarıyla çıkış yaptınız!', 'success')
    logger.info("Admin çıkış yaptı")
    return redirect(url_for('user.index'))

# Başvurular
@admin_bp.route('/basvurular')
def admin_basvurular():
    try:
        basvurular = db.basvurulari_listele(limit=50)
        for basvuru in basvurular:
            basvuru['yas'] = hesapla_yas(basvuru.get('dogum_tarihi'))
            basvuru['basvuru_tarihi_formatted'] = format_tarih(basvuru.get('basvuru_tarihi'))
        return render_template('admin_basvurular.html', basvurular=basvurular)
    except Exception as e:
        logger.error(f"Admin başvuru listesi hatası: {e}")
        flash('Başvurular yüklenirken hata oluştu!', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/basvuru/<int:basvuru_id>')
def admin_basvuru_detay(basvuru_id):
    try:
        basvuru = db.basvuru_getir(basvuru_id)
        if basvuru:
            basvuru['yas'] = hesapla_yas(basvuru.get('dogum_tarihi'))
            basvuru['basvuru_tarihi_formatted'] = format_tarih(basvuru.get('basvuru_tarihi'))
            return render_template('admin_basvuru_detay.html', basvuru=basvuru)
        else:
            flash('Başvuru bulunamadı!', 'error')
            return redirect(url_for('admin.admin_basvurular'))
    except Exception as e:
        logger.error(f"Başvuru detay hatası: {e}")
        flash('Başvuru detayı yüklenirken hata oluştu!', 'error')
        return redirect(url_for('admin.admin_basvurular'))

@admin_bp.route('/basvuru/<int:basvuru_id>/delete', methods=['POST'])
def admin_basvuru_sil(basvuru_id):
    try:
        if db.basvuru_sil(basvuru_id):
            flash('Başvuru başarıyla silindi!', 'success')
        else:
            flash('Başvuru silinirken hata oluştu!', 'error')
    except Exception as e:
        logger.error(f"Başvuru silme hatası: {e}")
        flash('Başvuru silinirken hata oluştu!', 'error')
    return redirect(url_for('admin.admin_basvurular'))

@admin_bp.route('/basvuru/<int:basvuru_id>/convert-to-student', methods=['POST'])
def admin_basvuru_ogrenciye_cevir(basvuru_id):
    flash('Bu özellik devre dışı.', 'warning')
    return redirect(url_for('admin.admin_basvurular'))

@admin_bp.route('/basvurular/bulk-delete', methods=['POST'])
def admin_basvuru_toplu_sil():
    ids = request.form.getlist('basvuru_ids')
    if not ids:
        flash('Hiçbir başvuru seçilmedi!', 'warning')
        return redirect(url_for('admin.admin_basvurular'))
    silinen = 0
    for id_str in ids:
        try:
            basvuru_id = int(id_str)
            if db.basvuru_sil(basvuru_id):
                silinen += 1
        except Exception as e:
            logger.error(f"Toplu silme sırasında hata: {e}")
    flash(f'{silinen} başvuru başarıyla silindi!', 'success' if silinen else 'warning')
    return redirect(url_for('admin.admin_basvurular'))

# Dekont analizleri
@admin_bp.route('/dekont-analizleri')
def admin_dekont_analizleri():
    try:
        dekont_analizleri = db.dekont_analizleri_listele(limit=50)
        return render_template('admin_dekont_analizleri.html', dekont_analizleri=dekont_analizleri)
    except Exception as e:
        logger.error(f"Admin dekont analizleri hatası: {e}")
        flash('Dekont analizleri yüklenirken hata oluştu!', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/ekstre-yukle', methods=['GET', 'POST'])
def admin_ekstre_yukle():
    EKSTRE_FOLDER = Path(current_app.config['UPLOAD_FOLDER']) / 'ekstreler'
    if request.method == 'POST':
        if 'ekstre_pdf' not in request.files:
            flash('Dosya seçilmedi!', 'error')
            return redirect(request.url)
        file = request.files['ekstre_pdf']
        if file.filename == '':
            flash('Dosya seçilmedi!', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename) and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            EKSTRE_FOLDER.mkdir(exist_ok=True, parents=True)
            file_path = EKSTRE_FOLDER / unique_filename
            file.save(str(file_path))
            flash('Ekstre başarıyla yüklendi!', 'success')
            return redirect(url_for('admin.admin_ekstre_yukle'))
        else:
            flash('Sadece PDF dosyası yükleyebilirsiniz!', 'error')
            return redirect(request.url)
    ekstreler = []
    if EKSTRE_FOLDER.exists():
        for f in EKSTRE_FOLDER.iterdir():
            if f.is_file() and f.name.lower().endswith('.pdf'):
                ekstreler.append(f.name)
    return render_template('admin_ekstre_yukle.html', ekstreler=sorted(ekstreler, reverse=True))

@admin_bp.route('/api/dekont-analiz/<int:analiz_id>')
def api_dekont_analiz_getir(analiz_id):
    try:
        analiz = db.dekont_analizi_getir(analiz_id)
        if analiz:
            basvuru = db.basvuru_getir(analiz['basvuru_id'])
            if basvuru:
                analiz.update({
                    'ad': basvuru['ad'],
                    'soyad': basvuru['soyad'],
                    'telefon': basvuru['telefon'],
                    'eposta': basvuru['eposta']
                })
            return jsonify(analiz)
        else:
            return jsonify({'error': 'Dekont analizi bulunamadı'}), 404
    except Exception as e:
        logger.error(f"API dekont analiz getirme hatası: {e}")
        return jsonify({'error': 'Sunucu hatası'}), 500
