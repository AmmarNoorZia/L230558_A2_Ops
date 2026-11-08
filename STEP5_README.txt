VISIONGUARD / STEP 5 - DOCKER, POSTGRESQL, COMPOSE, BASIC CI

Copy ONLY the CONTENTS of this package into the existing project root.
Do not replace or delete webapp, models, instance, .venv, .env or data.
This package has only NEW files; its scripts/ entries are additions.

PRECHECK
* Docker Desktop for Windows must be installed AND RUNNING using Linux containers.
* Keep models/champion.keras and webapp/app.py in their original locations.
* Existing Flask uses localhost:5000; Docker uses localhost:5001 to avoid conflicts.

RUN IN ORDER
15_DOCKER_CHECK.bat        -> verify Docker, generate .env.compose with random secrets
18_DOCKER_WARMUP.bat       -> Task 6.1 evidence, optional before building
16_DOCKER_BUILD_START.bat  -> build image, start PostgreSQL + web, wait for health
17_DOCKER_VERIFY.bat       -> check non-root execution + actual inference and history
19_DOCKER_OPERATIONS.bat   -> service status/logs/restart/shell demo
20_DOCKER_STOP.bat         -> optional clean shutdown (preserves PostgreSQL data)

Dockerfile uses a CPU-only TensorFlow wheel, Python 3.11 slim, separate
dependency layer, non-root user, Gunicorn and a health check. It does not
copy the raw dataset, model, token, .env or local .venv into the image.
compose.yaml defines 2 services: 'web' and 'database'. DB is private
to the Compose network; PostgreSQL data is kept in a named volume.
The existing SQLite history is not migrated: Docker uses a NEW PostgreSQL
history database, so the Docker History page starts empty.

DO NOT stage .env.compose or any tokens in GitHub. 15_DOCKER_CHECK adds it
to .gitignore. Commit the safe Dockerfile/compose.yaml/requirements files.

GITHUB ACTIONS
.github/workflows/visionguard-ci.yml is included. It builds the Docker
image and runs lightweight checks without needing an untracked Keras model.
The assignment ALSO requires a separate toy GitHub Actions red/green demo.
Instructions for that are in ci-toy-demo/README.md.

EVIDENCE TO COLLECT
(a) warm-up run/logs/exec; (b) docker compose ps showing healthy web and
db; (c) curl/browser http://127.0.0.1:5001/health; (d) inference + history;
(e) image sizes and non-root user; (f) operations and troubleshooting.
No live cloud API is deployed by this step. That is the next task.
