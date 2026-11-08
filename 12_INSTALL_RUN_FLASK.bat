@echo off
setlocal
cd /d "%~dp0"
echo [VisionGuard] Installing Flask application dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements-step4.txt
if errorlevel 1 (
  echo ERROR: Dependency installation failed. Check your internet connection and rerun.
  pause
  exit /b 1
)
echo.
echo [VisionGuard] Starting the local web app at http://127.0.0.1:5000
echo Keep this window open while using the app. Press Ctrl+C to stop.
".venv\Scripts\python.exe" run_flask.py
if errorlevel 1 (echo ERROR: Application could not start. & pause)
