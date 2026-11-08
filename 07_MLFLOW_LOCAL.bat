@echo off
setlocal
cd /d "%~dp0"
set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" (echo ERROR: Missing virtual environment. Keep the original project folder name.& pause & exit /b 1)
echo [VisionGuard] Installing Step 3 libraries and logging existing real training runs...
"%PY%" -m pip install -r requirements-step3.txt
if errorlevel 1 (echo ERROR: Package installation failed. & pause & exit /b 1)
"%PY%" scripts\mlflow_step3.py local
if errorlevel 1 (echo ERROR: Logging failed. & pause & exit /b 1)
echo.
echo SUCCESS: MLflow toy lab and imported training results logged locally.
echo Next: run 08_THREE_NEW_RUNS.bat
pause
