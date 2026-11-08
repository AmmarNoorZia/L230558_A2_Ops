@echo off
setlocal
cd /d "%~dp0"
echo Checking Docker Desktop and preparing Compose configuration...
where docker >nul 2>&1
if errorlevel 1 (
  echo Docker command not found. Install Docker Desktop for Windows and open it first.
  echo https://docs.docker.com/desktop/setup/install/windows-install/
  pause
  exit /b 1
)
docker version --format "{{.Server.Version}}"
if errorlevel 1 (
  echo Docker Desktop engine is not running. Start Docker Desktop and retry.
  pause
  exit /b 1
)
docker compose version
if errorlevel 1 (
  echo Docker Compose plugin is not available.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Existing project Python environment missing.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "scripts\create_compose_env.py"
if errorlevel 1 (pause & exit /b 1)
docker compose --env-file .env.compose config --quiet
if errorlevel 1 (
  echo Compose validation failed.
  pause
  exit /b 1
)
echo.
echo SUCCESS: Docker is available, secrets and configuration are ready.
echo NEXT: Run 16_DOCKER_BUILD_START.bat
pause
