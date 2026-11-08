VISIONGUARD STEP 4 — FLASK UI + DATABASE (TASKS 4 AND 5)
==========================================================

1. Extract this ZIP.
2. Copy ALL its contents into the EXISTING L230558_A2_MLOps folder.
   NEW: webapp/ folder, run_flask.py, requirements-step4.txt, and 12/13/14 .bat files.
   Existing models/, data/, scripts/, .env, and .venv stay untouched.
3. Double-click 12_INSTALL_RUN_FLASK.bat (installs only missing web dependencies).
4. Open http://127.0.0.1:5000 in a browser while the terminal remains open.
5. Upload one of the dataset JPG or PNG images. Open Result, History, /health.
6. Use screenshots for these pages (Task 4.2/4.3 and Task 5 evidence).
7. When finished, Ctrl+C stops the server.
8. To launch later, use 13_START_FLASK.bat (no reinstall).
9. For basic automated verification use 14_VERIFY_FLASK.bat (server need not be running).

IMPORTANT
- Uses your real models/champion.keras and champion_metadata.json from Task 2.
- Training preprocessing is matched: 0..255 RGB, 128x128 aspect-preserving resize_with_pad,
  and saved model contains its own normalization.
- Images remain in memory; database stores file name, verdict, time, model and confidence.
- Local history database: instance/visionguard.sqlite3 (not the model or MLflow database).
- .env already contains DagsHub credentials; do not replace it or publish it.
- Max file size default 8 MB. Allowed image types: JPG, PNG, WEBP.
- Optional PREDICTION_API_URL may be set later for Tasks 7/8 (hosted inference).
- Only SQLite is used for local development. PostgreSQL will be used with Docker Compose.
- Debug mode disabled.
- Remember: present real observations and acknowledge any AI assistance in report.

Next after local app works: Step 5 (Docker Compose / hosted inference API / CI).
