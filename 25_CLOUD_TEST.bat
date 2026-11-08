@echo off
setlocal
cd /d "%~dp0"
echo Testing real hosted inference using the project dataset...
".venv\Scripts\python.exe" cloud\test_cloud.py
if errorlevel 1 (echo ERROR: Cloud API test did not complete. & pause & exit /b 1)
pause
