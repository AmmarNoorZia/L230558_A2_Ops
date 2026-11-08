"""Fast integration tests. Use installed dependencies and actual model for one prediction."""
import io
import os
import unittest
from pathlib import Path
from PIL import Image

# Local SQLite test storage, separate from the app's real history.
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('DATABASE_URL', f'sqlite:///{(ROOT / "instance" / "visionguard_test.sqlite3").as_posix()}')
from webapp.app import create_app

class WebAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'ok')

    def test_home_and_history(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/history').status_code, 200)

    def test_invalid_file(self):
        response = self.client.post('/predict', data={'file': (io.BytesIO(b'not really an image'), 'fake.png')}, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)

    def test_wrong_extension(self):
        response = self.client.post('/predict', data={'file': (io.BytesIO(b'fake'), 'fake.exe')}, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)

    def test_real_prediction_and_history(self):
        buff = io.BytesIO()
        Image.new('RGB', (140, 100), (120, 100, 180)).save(buff, format='PNG')
        response = self.client.post('/predict', data={'file': (io.BytesIO(buff.getvalue()), 'sample.png')}, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 303)
        self.assertIn('/result/', response.headers['Location'])
        self.assertEqual(self.client.get(response.headers['Location']).status_code, 200)
        self.assertIn(b'sample.png', self.client.get('/history').data)

if __name__ == '__main__':
    unittest.main()
