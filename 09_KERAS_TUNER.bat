@echo off
setlocal
cd /d "%~dp0"
set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" (echo ERROR: Missing virtual environment.&pause&exit /b 1)
echo [VisionGuard] Keras Tuner toy experiment + 8 genuine VisionGuard search trials...
"%PY%" scripts\tuner_step3.py
if errorlevel 1 (echo ERROR: Tuner failed. Send screenshot.&pause&exit /b 1)
echo SUCCESS: Tuner results recorded in outputs\tuning_results.csv
pause
