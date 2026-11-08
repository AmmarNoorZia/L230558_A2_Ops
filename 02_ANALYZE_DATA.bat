@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Run 01_SETUP.bat first.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python scripts\audit_and_eda.py --data-dir data/raw --per-class 600
if errorlevel 1 (
  echo ANALYSIS FAILED: send me the last 20 lines.
  pause
  exit /b 1
)
echo.
echo SUCCESS: Audit, EDA, splits and notes saved to outputs\
echo Open outputs\ for charts and data summaries. SCREENSHOT the final output.
pause
