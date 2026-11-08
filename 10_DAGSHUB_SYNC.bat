@echo off
setlocal
cd /d "%~dp0"
set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" (echo ERROR: Missing virtual environment.&pause&exit /b 1)
if not exist ".env" (
 echo ERROR: Create .env in project root from STEP3_README.txt instructions.
 pause
 exit /b 1
)
"%PY%" scripts\mlflow_step3.py remote
if errorlevel 1 (echo ERROR: Remote DagsHub logging failed. Send screenshot WITHOUT token.&pause&exit /b 1)
echo SUCCESS: Training runs synchronized to DagsHub MLflow.
pause
