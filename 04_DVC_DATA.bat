@echo off
setlocal
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python scripts\dvc_track_dataset.py
if errorlevel 1 echo DVC data tracking failed. Send the error screenshot.
pause
