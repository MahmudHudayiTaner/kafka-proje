from flask import send_from_directory, current_app
from pathlib import Path
from . import uploads_bp
import logging

@uploads_bp.route('/<path:filename>')
def uploaded_file(filename):
    try:
        base_upload_folder = Path(current_app.root_path).parent / 'uploads'
        if filename.startswith('dekontlar/'):
            upload_folder = base_upload_folder / 'dekontlar'
            real_filename = filename[len('dekontlar/'):]
        elif filename.startswith('ekstreler/'):
            upload_folder = base_upload_folder / 'ekstreler'
            real_filename = filename[len('ekstreler/'):]
        else:
            upload_folder = base_upload_folder
            real_filename = filename
        return send_from_directory(str(upload_folder), real_filename)
    except Exception as e:
        logging.error(f"Dosya serve etme hatası: {e}")
        return "Dosya bulunamadı", 404
