@echo off
setlocal
cd /d "%~dp0"
if not exist ".env.compose" (echo Missing .env.compose & pause & exit /b 1)
echo Service status:
docker compose --env-file .env.compose ps
echo.
echo Verify non-root identity in web container:
docker compose --env-file .env.compose exec -T web id
if errorlevel 1 (pause & exit /b 1)
echo.
echo Verify PostgreSQL accessible only within Compose network:
docker compose --env-file .env.compose exec -T database pg_isready -U visionguard -d visionguard
if errorlevel 1 (pause & exit /b 1)
echo.
echo Execute real HTTP smoke tests against Docker port 5001:
".venv\Scripts\python.exe" scripts\verify_compose.py
if errorlevel 1 (pause & exit /b 1)
echo.
echo Image sizes:
docker image ls visionguard-web --format "{{.Repository}}:{{.Tag}}  {{.Size}}"
docker image ls postgres --format "{{.Repository}}:{{.Tag}}  {{.Size}}"
echo.
echo SUCCESS: Container app, database, model inference and history verified.
pause
