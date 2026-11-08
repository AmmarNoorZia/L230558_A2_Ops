@echo off
setlocal
cd /d "%~dp0"
set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" (echo ERROR: Missing virtual environment.&pause&exit /b 1)
echo [VisionGuard] Training 3 ADDITIONAL real experiments; logging live epoch metrics to MLflow...
"%PY%" scripts\mlflow_step3.py experiments
if errorlevel 1 (echo ERROR: Some experiments failed.&pause&exit /b 1)
echo SUCCESS: Six or more distinct training configurations are available in MLflow.
pause
