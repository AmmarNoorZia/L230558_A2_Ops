"""Sets the existing local Flask UI to call the verified cloud API."""
from pathlib import Path
from urllib.parse import urlparse
import requests

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / '.env'

url = input('Paste Modal public URL (ends with modal.run): ').strip().rstrip('/')
if url.endswith('/predict'):
    url = url[:-len('/predict')]
parsed = urlparse(url)
if parsed.scheme != 'https' or not parsed.netloc.endswith('.modal.run'):
    raise SystemExit('Expected an HTTPS Modal URL ending in .modal.run')
health_url = url + '/health'
print('Checking public health:', health_url)
res = requests.get(health_url, timeout=100)
res.raise_for_status()
health = res.json()
if health.get('status') != 'ok':
    raise SystemExit('Unexpected health response; no configuration changed')
print('Cloud API healthy:', health)
previous = ENV.read_text(encoding='utf-8') if ENV.exists() else ''
lines = [line for line in previous.splitlines() if not line.strip().startswith('PREDICTION_API_URL=')]
lines.append('PREDICTION_API_URL=' + url + '/predict')
ENV.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
print('SUCCESS: Local Flask configured to call the cloud model API.')
print('NEXT: Close the local Flask server and start 13_START_FLASK.bat again.')
print('Visit http://127.0.0.1:5000/health and confirm model_source is cloud-api.')
