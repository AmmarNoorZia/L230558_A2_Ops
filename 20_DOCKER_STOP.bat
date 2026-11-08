@echo off
setlocal
cd /d "%~dp0"
docker compose --env-file .env.compose down
echo Docker containers stopped. Named PostgreSQL volume retained.
pause
