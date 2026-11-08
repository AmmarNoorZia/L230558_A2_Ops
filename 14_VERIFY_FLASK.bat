@echo off
setlocal
cd /d "%~dp0"
echo [VisionGuard] Testing health, input validation, live prediction and history.
".venv\Scripts\python.exe" -m unittest discover -s tests -p test_webapp.py -v
if errorlevel 1 (echo ERROR: A test did not pass. & pause & exit /b 1)
echo SUCCESS: Flask application smoke tests passed.
pause
