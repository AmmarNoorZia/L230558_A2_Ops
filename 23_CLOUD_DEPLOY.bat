@echo off
setlocal
cd /d "%~dp0"
echo Deploying L230558_A2_Ops to Modal...
".venv\Scripts\modal.exe" deploy cloud\modal_api.py
if errorlevel 1 (echo ERROR: Cloud deployment failed. & pause & exit /b 1)
echo SUCCESS: Cloud application deployed.
echo COPY the public URL shown above. It ends in .modal.run
pause
