@echo off
setlocal
cd /d "%~dp0"
echo Open http://127.0.0.1:5000 in a browser once server starts. Ctrl+C to stop.
".venv\Scripts\python.exe" -m mlflow ui --backend-store-uri "sqlite:///mlflow.db" --host 127.0.0.1 --port 5000
pause
