"""Exercise Compose-hosted Flask and PostgreSQL through real HTTP requests."""
import io
import requests
from PIL import Image
BASE = 'http://127.0.0.1:5001'
for endpoint in ('/', '/history', '/health'):
    response = requests.get(BASE + endpoint, timeout=30)
    response.raise_for_status()
    print(f'GET {endpoint}: {response.status_code}')
    if endpoint == '/health':
        data = response.json()
        assert data['status'] == 'ok' and data['database'] == 'connected', data
fake = requests.post(BASE + '/predict', files={'file': ('invalid.png', b'not an image', 'image/png')}, timeout=30)
assert fake.status_code == 400, f'Invalid data not rejected: {fake.status_code}'
print('POST /predict (invalid): 400, rejected')
png = io.BytesIO()
Image.new('RGB', (128, 128), color=(117, 143, 164)).save(png, format='PNG')
response = requests.post(BASE + '/predict', files={'file': ('compose_test.png', png.getvalue(), 'image/png')}, timeout=120, allow_redirects=False)
assert response.status_code == 303, f'Inference failed: {response.status_code} {response.text[:350]}'
destination = response.headers['Location']
result = requests.get(BASE + destination, timeout=30)
result.raise_for_status()
history = requests.get(BASE + '/history', timeout=30)
history.raise_for_status()
assert 'compose_test.png' in history.text, 'Database history missing uploaded prediction'
print('POST /predict (real inference): 303 -> result: 200')
print('GET /history: prediction stored in PostgreSQL')
print('SUCCESS: Docker Compose end-to-end test passed.')
