"""Single-load Keras inference matching Task 2 input processing.

Training: RGB image -> tf.image.resize_with_pad(..., 128, 128), 0..255 floats.
Normalization is *inside* the saved model. Never normalize externally again.
"""
from __future__ import annotations
import io
import json
import os
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
MAX_PIXELS = 24_000_000
Image.MAX_IMAGE_PIXELS = MAX_PIXELS
SUPPORTED = {'JPEG', 'PNG', 'WEBP'}

class ImageValidationError(ValueError):
    pass


def decode_upload(content: bytes, extension: str):
    """Validate magic bytes and decode fully; never write uploaded data to disk."""
    if not content:
        raise ImageValidationError('Choose an image before submitting.')
    ext = extension.lower().lstrip('.')
    if ext not in {'jpg', 'jpeg', 'png', 'webp'}:
        raise ImageValidationError('Supported file types: JPG, PNG and WEBP.')
    try:
        with Image.open(io.BytesIO(content)) as check:
            actual = check.format
            width, height = check.size
            if actual not in SUPPORTED:
                raise ImageValidationError('File contents are not a supported image format.')
            if width * height > MAX_PIXELS:
                raise ImageValidationError('Image dimensions are too large.')
            if actual == 'JPEG' and ext not in {'jpg', 'jpeg'}:
                raise ImageValidationError('File extension does not match image contents.')
            if actual in {'PNG', 'WEBP'} and ext != actual.lower():
                raise ImageValidationError('File extension does not match image contents.')
            check.verify()
        with Image.open(io.BytesIO(content)) as source:
            image = ImageOps.exif_transpose(source)
            rgb = image.convert('RGB')
            rgb.load()  # Ensure broken/truncated payloads are detected.
            return rgb
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        if isinstance(exc, ImageValidationError):
            raise
        raise ImageValidationError('The image is damaged or cannot be decoded.') from exc


@lru_cache(maxsize=1)
def load_predictor():
    """Load once per serving process, not for every request."""
    import tensorflow as tf
    model_path = Path(os.getenv('MODEL_PATH', str(ROOT / 'models' / 'champion.keras')))
    if not model_path.is_file():
        raise FileNotFoundError(f'Champion model is missing: {model_path}')
    model = tf.keras.models.load_model(str(model_path), compile=False)
    metadata_path = Path(os.getenv('MODEL_METADATA_PATH', str(ROOT / 'models' / 'champion_metadata.json')))
    metadata = json.loads(metadata_path.read_text(encoding='utf-8')) if metadata_path.is_file() else {}
    threshold = float(os.getenv('MODEL_THRESHOLD', metadata.get('threshold', 0.5)))
    if not 0 <= threshold <= 1:
        raise ValueError('MODEL_THRESHOLD must lie between 0 and 1')
    return model, threshold, str(metadata.get('version', 'champion')), int(metadata.get('image_size', 128))


def predict(image):
    import numpy as np
    import tensorflow as tf
    model, threshold, version, image_size = load_predictor()
    pixels = tf.convert_to_tensor(np.asarray(image, dtype=np.float32))
    pixels = tf.image.resize_with_pad(pixels, image_size, image_size)
    batch = tf.expand_dims(pixels, axis=0)
    ai_probability = float(np.asarray(model.predict(batch, verbose=0)).reshape(-1)[0])
    is_ai = ai_probability >= threshold
    return {
        'label': 'AI-generated' if is_ai else 'Real',
        'ai_probability': round(ai_probability, 6),
        'confidence': round(ai_probability if is_ai else 1.0 - ai_probability, 6),
        'threshold': threshold,
        'model_version': version,
        'disclaimer': 'This is a model estimate, not proof of an image\'s origin.'
    }
