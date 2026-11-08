@echo off
setlocal
cd /d "%~dp0"
echo VisionGuard local web interface: http://127.0.0.1:5000
".venv\Scripts\python.exe" run_flask.py
if errorlevel 1 pause
