# Kullanıcı işlemleri için route'lar burada tanımlanır
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from src.core.database import get_database
from src.core.logger import get_logger
from src.models.basvuru import Basvuru
from src.utils.validators import validate_basvuru_data, sanitize_name, sanitize_phone
import threading

user_bp = Blueprint('user', __name__)

db = get_database()
logger = get_logger("web_app")

def analyze_pdf_in_background(basvuru_id, pdf_dosya_yolu):
    try:
        from src.services.pdf_analyzer import get_pdf_analyzer
        pdf_analyzer = get_pdf_analyzer()
        from pathlib import Path
        db = get_database()
        full_pdf_path = str(Path('uploads') / 'dekontlar' / pdf_dosya_yolu)
        analiz_sonucu = pdf_analyzer.analyze_dekont(full_pdf_path)
        if analiz_sonucu:
            analiz_data = {
                'basvuru_id': basvuru_id,
                'pdf_dosya_yolu': pdf_dosya_yolu,
                'sender_name': analiz_sonucu.get('sender_name'),
                'amount': analiz_sonucu.get('amount'),
                'bank_name': analiz_sonucu.get('bank_name'),
                'date': analiz_sonucu.get('date'),
                'time': analiz_sonucu.get('time'),
                'extraction_date': analiz_sonucu.get('extraction_date'),
                'raw_text': analiz_sonucu.get('raw_text'),
                'confidence_score': analiz_sonucu.get('confidence_score', 0.8),
                'ai_used': analiz_sonucu.get('ai_used', False)
            }
            db.dekont_analizi_ekle(analiz_data)
    except Exception as e:
        logger.error(f"Arka planda PDF analizi hatası: {e}")

@user_bp.route('/')
def index():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('index.html')

@user_bp.route('/submit', methods=['POST'])
def submit_basvuru():
    try:
        basvuru_data = {
            'ad': sanitize_name(request.form.get('ad', '').strip()),
            'soyad': sanitize_name(request.form.get('soyad', '').strip()),
            'telefon': sanitize_phone(request.form.get('telefon', '').strip()),
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
        if 'pdf_dosya' in request.files:
            file = request.files['pdf_dosya']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                dekontlar_path = Path('uploads') / 'dekontlar'
                dekontlar_path.mkdir(exist_ok=True, parents=True)
                file_path = dekontlar_path / filename
                file.save(str(file_path))
                basvuru_data['pdf_dosya_yolu'] = filename
                logger.info(f"PDF dekontu yüklendi: dekontlar/{filename}")
        is_valid, error = validate_basvuru_data(basvuru_data)
        if not is_valid:
            flash(f'Form hatası: {error}', 'error')
            return redirect(url_for('user.index'))
        basvuru = Basvuru(**basvuru_data)
        basvuru_id = db.basvuru_ekle(basvuru.to_dict())
        if basvuru_id and basvuru_data['pdf_dosya_yolu']:
            threading.Thread(target=analyze_pdf_in_background, args=(basvuru_id, basvuru_data['pdf_dosya_yolu'])).start()
        if basvuru_id:
            flash(f'Başvurunuz başarıyla kaydedildi!', 'success')
            logger.info(f"Yeni başvuru kaydedildi: ID={basvuru_id}, Ad={basvuru.tam_ad()}")
        else:
            if basvuru_data.get('eposta'):
                flash('Bu email adresi ile daha önce başvuru yapılmış! Her email adresi ile sadece bir kez başvuru yapılabilir.', 'error')
            else:
                flash('Başvuru kaydedilirken bir hata oluştu!', 'error')
            logger.error("Başvuru kaydedilemedi")
        return redirect(url_for('user.index'))
    except Exception as e:
        logger.error(f"Başvuru gönderimi hatası: {e}")
        flash('Beklenmeyen bir hata oluştu!', 'error')
        return redirect(url_for('user.index'))
