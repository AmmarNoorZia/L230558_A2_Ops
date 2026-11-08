@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Missing virtual environment. Run 01_SETUP.bat first.
  pause
  exit /b 1
)
echo [VisionGuard] Training baseline CNN using dataset splits from Step 1...
.venv\Scripts\python.exe scripts\train_models.py --mode baseline
if errorlevel 1 goto fail
echo.
echo SUCCESS: Baseline CNN finished. Take a screenshot and start 06_TRAIN_TRANSFER.bat
pause
exit /b 0
:fail
echo.
echo ERROR: Copy the last 25 terminal lines and send them to ChatGPT.
pause
exit /b 1
