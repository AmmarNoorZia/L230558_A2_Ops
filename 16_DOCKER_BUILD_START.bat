@echo off
setlocal
cd /d "%~dp0"
if not exist ".env.compose" (
  echo Run 15_DOCKER_CHECK.bat first.
  pause
  exit /b 1
)
echo Building the VisionGuard CPU inference image...
docker compose --env-file .env.compose build web
if errorlevel 1 (
  echo ERROR: Docker build failed. Capture the first relevant ERROR line.
  pause
  exit /b 1
)
echo Starting isolated PostgreSQL and web containers...
docker compose --env-file .env.compose up -d --wait --wait-timeout 240
if errorlevel 1 (
  echo ERROR: Containers did not reach healthy state. Showing recent logs...
  docker compose --env-file .env.compose ps
  docker compose --env-file .env.compose logs --tail=60
  pause
  exit /b 1
)
docker compose --env-file .env.compose ps
echo.
echo SUCCESS: Docker Compose stack is running at http://127.0.0.1:5001
echo NEXT: Run 17_DOCKER_VERIFY.bat
pause
