@echo off
setlocal
cd /d "%~dp0"
echo Docker exercise: image, container, port, volume, logs, exec, list, cleanup.
docker rm -f vg-warmup >nul 2>&1
echo [1] docker run, publish local port, mount named volume:
docker run -d --name vg-warmup -p 127.0.0.1:8099:80 -v vg_warmup:/var/cache/nginx nginx:alpine
if errorlevel 1 (pause & exit /b 1)
echo [2] Container list:
docker ps --filter name=vg-warmup
echo [3] Container logs:
docker logs --tail=8 vg-warmup
echo [4] Shell command inside the container:
docker exec vg-warmup sh -c "whoami; ls /var/cache/nginx"
echo [5] Volume and image list:
docker volume ls --filter name=vg_warmup
docker image ls nginx
echo [6] Stop and remove container:
docker stop vg-warmup
docker rm vg-warmup
echo SUCCESS: Docker warm-up completed. Volume and image deliberately retained for evidence.
pause
