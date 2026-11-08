@echo off
setlocal
cd /d "%~dp0"
echo Installing Modal SDK in the current project environment...
".venv\Scripts\python.exe" -m pip install "modal>=1.6.3,<2"
if errorlevel 1 (echo ERROR: Modal installation failed. & pause & exit /b 1)
echo SUCCESS: Modal CLI installed.
pause
