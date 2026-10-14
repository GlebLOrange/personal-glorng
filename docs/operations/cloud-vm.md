# Cursor Cloud VM

Cloud-Agent-only facts. Local Docker does not need this file.

## Docker daemon

Not auto-started. Once per session:

```bash
sudo dockerd > /tmp/dockerd.log 2>&1 &
# wait until: docker info
```

Daemon uses `fuse-overlayfs` and `default-cgroupns-mode: host` in `/etc/docker/daemon.json`. On Docker 29+, also set `"features": {"containerd-snapshotter": false}` or `fuse-overlayfs` is ignored.

## Compose overlay

Nested Docker cannot apply Compose `deploy.resources` (cgroupv2 threaded mode). Always include `-f docker-compose.cloud-vm.yml`. That overlay must reset `deploy` and set `cgroup: host` for **every** service you start — including `mongodb` and `rabbitmq` — or containers fail with `cannot enter cgroupv2 ... it is in threaded mode`.

```bash
# Lite: API in Docker (no RabbitMQ / client container)
docker compose -f docker-compose.yml -f docker-compose.lite.yml -f docker-compose.cloud-vm.yml up -d mongodb redis redis-cache server nginx

# Ultra-lite: host API
docker compose -f docker-compose.yml -f docker-compose.ultra-lite.yml -f docker-compose.cloud-vm.yml up -d mongodb redis
make dev-ultra-lite-server
```

Equivalent to `make dev-lite` / `make dev-ultra-lite-infra` plus the cloud overlay.

Elasticsearch search: add `-f docker-compose.search.yml` and `--profile search`, and set `ELASTICSEARCH_URL=http://elasticsearch:9200` in `.env`. Leave `ELASTICSEARCH_URL` empty for lite mode.

## Host backend checks

Docker may mount `server/.venv`. Use an isolated venv (matches CI backend job):

```bash
export PATH="$HOME/.local/bin:$PATH"
cd server
UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv sync --frozen
UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv run ruff check .
GLORNG_ENV_FILE=$PWD/tests/.env.test \
UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv run pytest -v
```

Prod images do not include `pytest`/`ruff`; host `uv` is the canonical path for backend checks.

## Node

Need Node 24 (`.nvmrc` / `client` engines). Cloud VM `/exec-daemon/node` is often v22 — prepend `"$HOME/.nvm/versions/node/v24.18.0/bin"` to `PATH` or `nvm use` before client lint/test/build.

Canonical local commands: [Getting started](/guide/getting-started), [Contributing](/guide/contributing).
