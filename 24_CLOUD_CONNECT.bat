@echo off
setlocal
cd /d "%~dp0"
echo Connecting existing Flask UI to Modal public API...
".venv\Scripts\python.exe" cloud\connect_cloud.py
if errorlevel 1 (echo ERROR: Cloud connection failed; existing config not changed. & pause & exit /b 1)
pause
