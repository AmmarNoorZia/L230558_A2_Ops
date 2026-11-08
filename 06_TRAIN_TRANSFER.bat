@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Missing virtual environment. Run 01_SETUP.bat first.
  pause
  exit /b 1
)
echo [VisionGuard] Training MobileNetV2 with frozen backbone, then fine tuning...
echo First run may need internet to download ImageNet backbone weights.
.venv\Scripts\python.exe scripts\train_models.py --mode transfer
if errorlevel 1 goto fail
echo.
echo SUCCESS: Transfer learning and champion selection finished.
echo Screenshots: console final results and outputs\*_curves.png.
pause
exit /b 0
:fail
echo.
echo ERROR: Copy the last 25 terminal lines and send them to ChatGPT.
pause
exit /b 1
