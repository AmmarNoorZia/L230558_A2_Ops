"""Assignment 1.1: record exact installed versions and TensorFlow GPU visibility."""
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import importlib.metadata as md

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
packages = ["tensorflow", "keras", "numpy", "pandas", "pillow", "matplotlib", "scikit-learn", "dvc", "kaggle", "python-dotenv"]
versions = {}
for package in packages:
    try:
        versions[package] = md.version(package)
    except md.PackageNotFoundError:
        versions[package] = "NOT INSTALLED"

import tensorflow as tf
info = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "python": sys.version,
    "platform": platform.platform(),
    "packages": versions,
    "tensorflow_gpu_devices": [str(d) for d in tf.config.list_physical_devices("GPU")],
    "tensorflow_cpu_devices": [str(d) for d in tf.config.list_physical_devices("CPU")],
}
(OUT / "environment.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
(OUT / "pip_freeze.txt").write_text(subprocess.check_output([sys.executable,"-m","pip","freeze"], text=True), encoding="utf-8")
print("=" * 56)
print("VISIONGUARD / TASK 1.1 - ENVIRONMENT REPORT")
print("Python:", platform.python_version())
for package, ver in versions.items():
    print(f"{package}: {ver}")
print("GPU devices:", info["tensorflow_gpu_devices"])
print("CPU devices:", info["tensorflow_cpu_devices"])
print("Files saved: outputs/environment.json, outputs/pip_freeze.txt")
print("=" * 56)
if os.name == "nt" and not info["tensorflow_gpu_devices"]:
    print("NOTE: CPU-only TensorFlow on native Windows is expected for TF >= 2.11.")
