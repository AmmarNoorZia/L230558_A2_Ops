@echo off
setlocal
cd /d "%~dp0"
if not exist ".env.compose" (echo Missing .env.compose & pause & exit /b 1)
echo Container operations demonstration:
echo [1] Status:
docker compose --env-file .env.compose ps
echo [2] Recent logs:
docker compose --env-file .env.compose logs --tail=10 web
echo [3] Restart web service:
docker compose --env-file .env.compose restart web
echo [4] Run shell command inside web service:
docker compose --env-file .env.compose exec -T web sh -c "id; python --version"
echo [5] Show full container/image metadata:
docker image inspect visionguard-web:local --format "{{.Size}} bytes"
echo SUCCESS: Operations demonstrated. Containers remain running.
pause
