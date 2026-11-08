@echo off
setlocal
cd /d "%~dp0"
echo Opening Modal login in your browser...
".venv\Scripts\modal.exe" setup
if errorlevel 1 (echo ERROR: Modal login failed. & pause & exit /b 1)
echo SUCCESS: Modal account is connected.
pause
