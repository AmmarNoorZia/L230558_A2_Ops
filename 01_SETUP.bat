@echo off
setlocal
cd /d "%~dp0"
echo [VisionGuard] Setting up isolated Python 3.11 environment...
py -3.11 --version >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python 3.11 x64 is required. Install it from python.org, then rerun.
  echo Check the "Add Python to PATH" checkbox during installation.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" py -3.11 -m venv .venv
if errorlevel 1 goto error
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto error
python -m pip install -r requirements-step1.txt
if errorlevel 1 goto error
python scripts\check_environment.py
if errorlevel 1 goto error
echo.
echo SUCCESS: environment is ready. SCREENSHOT this final output for 1.1.
pause
exit /b 0
:error
echo.
echo SETUP FAILED. Take a screenshot and send me the last 20 lines.
pause
exit /b 1
