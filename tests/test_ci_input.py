import io
import unittest
from PIL import Image
from webapp.inference import decode_upload, ImageValidationError

class ImageValidationTests(unittest.TestCase):
    def test_real_png_decodes(self):
        stream = io.BytesIO()
        Image.new('RGB', (32, 32)).save(stream, 'PNG')
        self.assertEqual(decode_upload(stream.getvalue(), 'png').mode, 'RGB')

    def test_corrupt_png_rejected(self):
        with self.assertRaises(ImageValidationError):
            decode_upload(b'not an image', 'png')

    def test_wrong_extension_rejected(self):
        with self.assertRaises(ImageValidationError):
            decode_upload(b'test', 'exe')

if __name__ == '__main__':
    unittest.main()
