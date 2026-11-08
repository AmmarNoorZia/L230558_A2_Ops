# VisionGuard production-style container, CPU inference, Python 3.11.
FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    TF_NUM_INTEROP_THREADS=2 \
    TF_NUM_INTRAOP_THREADS=2
WORKDIR /app
# Use a slim base with only required runtime libraries.
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*
# Dependencies ahead of source files for reliable Docker layer caching.
COPY requirements-docker.txt ./
RUN python -m pip install --no-cache-dir -r requirements-docker.txt
RUN groupadd --system vg && useradd --system --gid vg --home /app vg
COPY --chown=vg:vg webapp/ ./webapp/
# The application initializes a local instance path before connecting to PostgreSQL.
RUN mkdir -p /app/instance && chown -R vg:vg /app
USER vg
EXPOSE 5000
HEALTHCHECK --interval=20s --timeout=10s --start-period=90s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=8)" || exit 1
# The Keras model is mounted read-only by Compose, not baked into Git or the image.
CMD ["gunicorn", "--workers", "1", "--threads", "2", "--timeout", "120", "--bind", "0.0.0.0:5000", "webapp.app:create_app()"]
