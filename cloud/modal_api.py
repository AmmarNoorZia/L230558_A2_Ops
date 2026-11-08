"""VisionGuard cloud inference API for Modal.

The Keras model is mounted from models/champion.keras at deployment time.
Image preprocessing and output shape are identical to webapp/inference.py.
"""
# UploadFile must be resolved at route registration, not kept as a
# deferred string annotation in this nested Modal ASGI function.
from pathlib import Path

import modal

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_LOCAL = PROJECT_ROOT / "models" / "champion.keras"
METADATA_LOCAL = PROJECT_ROOT / "models" / "champion_metadata.json"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libgomp1")
    .uv_pip_install(
        "tensorflow-cpu==2.21.0",
        "fastapi>=0.115,<1",
        "python-multipart>=0.0.18",
        "pillow>=12,<13",
    )
)

# The developer's machine has the source model under models/.
# A Modal container has the uploaded model under /root/model/ instead.
# Only access source files while building the deployment locally.
if modal.is_local():
    if not MODEL_LOCAL.is_file():
        raise FileNotFoundError(f"Local champion model not found: {MODEL_LOCAL}")
    if not METADATA_LOCAL.is_file():
        raise FileNotFoundError(f"Local champion metadata not found: {METADATA_LOCAL}")
    image = (
        image
        .add_local_file(str(MODEL_LOCAL), "/root/model/champion.keras")
        .add_local_file(str(METADATA_LOCAL), "/root/model/champion_metadata.json")
    )

app = modal.App("L230558_A2_Ops", image=image)


@app.function(cpu=1, memory=4096, timeout=120)
@modal.asgi_app()
def api():
    import io
    import json
    from functools import lru_cache

    import numpy as np
    import tensorflow as tf
    from fastapi import FastAPI, File, HTTPException, UploadFile
    from PIL import Image, ImageOps, UnidentifiedImageError

    MAX_BYTES = 8 * 1024 * 1024
    MAX_PIXELS = 24_000_000
    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    web = FastAPI(title="VisionGuard Prediction API", version="1.0")

    @lru_cache(maxsize=1)
    def get_model():
        model = tf.keras.models.load_model("/root/model/champion.keras", compile=False)
        with open("/root/model/champion_metadata.json", encoding="utf-8") as f:
            metadata = json.load(f)
        threshold = float(metadata.get("threshold", 0.5))
        image_size = int(metadata.get("image_size", 128))
        version = str(metadata.get("version", "champion"))
        if not 0 <= threshold <= 1:
            raise ValueError("Invalid model threshold")
        return model, threshold, image_size, version

    @web.get("/")
    def index():
        return {"service": "VisionGuard", "endpoints": ["/health", "/predict", "/docs"]}

    @web.get("/health")
    def health():
        model, threshold, image_size, version = get_model()
        return {"status": "ok", "model_version": version, "image_size": image_size,
                "threshold": threshold, "backend": "tensorflow-cpu"}

    @web.post("/predict")
    async def predict(file: UploadFile = File(...)):
        filename = (file.filename or "").lower()
        ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
        if ext not in {"jpg", "jpeg", "png", "webp"}:
            raise HTTPException(status_code=400, detail="Use JPG, PNG or WEBP images")
        payload = await file.read(MAX_BYTES + 1)
        await file.close()
        if not payload or len(payload) > MAX_BYTES:
            raise HTTPException(status_code=413, detail="Image is empty or exceeds 8 MB")
        try:
            with Image.open(io.BytesIO(payload)) as probe:
                actual_format = probe.format
                w, h = probe.size
                if actual_format not in {"JPEG", "PNG", "WEBP"} or w * h > MAX_PIXELS:
                    raise ValueError("Unsupported image or dimensions")
                if actual_format == "JPEG" and ext not in {"jpg", "jpeg"}:
                    raise ValueError("File extension does not match contents")
                if actual_format in {"PNG", "WEBP"} and ext != actual_format.lower():
                    raise ValueError("File extension does not match contents")
                probe.verify()
            with Image.open(io.BytesIO(payload)) as src:
                rgb = ImageOps.exif_transpose(src).convert("RGB")
                rgb.load()
        except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError):
            raise HTTPException(status_code=400, detail="Unreadable or invalid image") from None

        model, threshold, size, version = get_model()
        tensor = tf.convert_to_tensor(np.asarray(rgb, dtype=np.float32))
        batch = tf.expand_dims(tf.image.resize_with_pad(tensor, size, size), axis=0)
        probability = float(np.asarray(model.predict(batch, verbose=0)).reshape(-1)[0])
        is_ai = probability >= threshold
        return {
            "label": "AI-generated" if is_ai else "Real",
            "ai_probability": round(probability, 6),
            "confidence": round(probability if is_ai else 1.0 - probability, 6),
            "threshold": threshold,
            "model_version": version,
            "disclaimer": "This is a model estimate, not proof of an image's origin.",
        }

    return web
