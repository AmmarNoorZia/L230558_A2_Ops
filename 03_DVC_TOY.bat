@echo off
setlocal
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python scripts\dvc_toy_demo.py
if errorlevel 1 echo DVC demo failed. Send the error screenshot.
pause
