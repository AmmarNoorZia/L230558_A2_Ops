"""Flask UI and JSON API. Image bytes are validated in memory and never persisted."""
from __future__ import annotations
import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from .database import database, database_healthy, get_prediction, history, store_prediction
from .inference import ImageValidationError, decode_upload, load_predictor, predict

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env', override=False)
MAX_UPLOAD_BYTES = int(os.getenv('MAX_UPLOAD_BYTES', str(8 * 1024 * 1024)))


def classify(content, filename):
    extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
    image = decode_upload(content, extension)
    cloud_url = os.getenv('PREDICTION_API_URL', '').strip()
    if cloud_url:
        # Cloud inference for Tasks 7–8. Local Flask remains the UI and logs history.
        token = os.getenv('PREDICTION_API_KEY', '')
        headers = {'X-API-Key': token} if token else {}
        mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}[extension.lower()]
        try:
            response = requests.post(cloud_url,
                files={'file': (filename, content, mime)},
                headers=headers, timeout=45)
            response.raise_for_status()
            remote = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise RuntimeError('Cloud inference API is unavailable. Check the API URL and connection.') from exc
        required = {'label', 'confidence', 'ai_probability', 'threshold', 'model_version'}
        if not required.issubset(remote) or remote['label'] not in {'Real', 'AI-generated'}:
            raise RuntimeError('Cloud API returned an unexpected prediction format.')
        return remote
    return predict(image)


def create_app():
    app = Flask(__name__, template_folder=str(ROOT / 'webapp' / 'templates'),
                static_folder=str(ROOT / 'webapp' / 'static'))
    app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_BYTES
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'local-development-only-change-for-deployment')
    app.config['JSON_SORT_KEYS'] = False
    database()  # Fail early on invalid database configuration.
    if not os.getenv('PREDICTION_API_URL', '').strip():
        load_predictor()  # Load champion once at app startup.

    @app.get('/')
    def home():
        return render_template('home.html', max_mb=MAX_UPLOAD_BYTES // (1024 * 1024))

    @app.post('/predict')
    def upload():
        file = request.files.get('file')
        if not file or not file.filename:
            return render_template('error.html', message='Select an image to analyze.'), 400
        safe_name = secure_filename(file.filename)
        if not safe_name:
            return render_template('error.html', message='Invalid file name.'), 400
        content = file.read(MAX_UPLOAD_BYTES + 1)
        if len(content) > MAX_UPLOAD_BYTES:
            return render_template('error.html', message='The file exceeds the upload size limit.'), 413
        try:
            result = classify(content, safe_name)
        except ImageValidationError as exc:
            return render_template('error.html', message=str(exc)), 400
        except Exception as exc:
            app.logger.exception('Prediction failed: %s', type(exc).__name__)
            return render_template('error.html', message='Prediction service is temporarily unavailable.'), 503
        record_id = store_prediction(safe_name, result)
        return redirect(url_for('result_page', record_id=record_id), code=303)

    @app.get('/result/<int:record_id>')
    def result_page(record_id):
        record = get_prediction(record_id)
        if record is None:
            return render_template('error.html', message='Prediction record was not found.'), 404
        return render_template('result.html', record=record)

    @app.get('/history')
    def history_page():
        return render_template('history.html', records=history())

    @app.get('/health')
    def health():
        try:
            database_healthy()
            model_source = 'cloud-api' if os.getenv('PREDICTION_API_URL') else 'local-champion'
            return jsonify({'status': 'ok', 'database': 'connected', 'model_source': model_source}), 200
        except Exception:
            return jsonify({'status': 'unhealthy'}), 503

    @app.errorhandler(413)
    def too_large(_):
        return render_template('error.html', message='This file is too large. Please upload a smaller image.'), 413

    @app.errorhandler(404)
    def not_found(_):
        return render_template('error.html', message='Page not found.'), 404

    return app
