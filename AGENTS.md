# AGENTS.md

## Cursor Cloud specific instructions

### Product overview

**gLOrng** is a FastAPI + Vue 3 developer portfolio and personal platform. The recommended dev workflow is **lite mode**: PostgreSQL, Redis, and the API in Docker; Vite on the host.

### Cloud VM Docker caveat

Nested Docker on Cloud Agent VMs cannot apply Compose `deploy.resources` memory limits (cgroupv2 threaded mode). Always include the cloud overlay when starting services:

```bash
docker compose -f docker-compose.yml -f docker-compose.lite.yml -f docker-compose.cloud-vm.yml up -d db redis server
```

Equivalent to `make dev-lite` with the overlay. Docker daemon on this VM also uses `fuse-overlayfs` and `default-cgroupns-mode: host` in `/etc/docker/daemon.json`.

### First-time / manual setup

1. Copy env: `cp .env.example .env` and set at minimum `JWT_SECRET` (32+ chars), `REDIS_PASSWORD`, and `SEED_PASSWORD`.
2. Start backend: command above (or `make dev-lite` plus the cloud overlay file).
3. Seed admin: `docker compose … exec server python scripts/ensure_e2e_user.py` (or `make seed` with `SEED_PASSWORD` set).
4. Frontend: `cd client && VITE_API_PROXY_TARGET=http://127.0.0.1:8000 npm run dev` → http://localhost:3000

Default E2E credentials: `admin@glorng.dev` / `MyTestPass123!`

### Services and ports

| Service | URL / port |
|---------|------------|
| API (lite) | http://127.0.0.1:8000 — docs at `/api/docs` |
| Vite (host) | http://localhost:3000 |
| PostgreSQL (host tools) | `127.0.0.1:5433` |

### Lint / test / build

See `README.md` for canonical commands. Cloud-specific notes:

- **Backend lint/tests (host, matches CI backend job):** use an isolated venv because Docker mounts `server/.venv`:
  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  cd server
  UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv sync --frozen
  UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv run ruff check .
  UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv DATABASE_URL='sqlite+aiosqlite:///./test.db' REDIS_URL='redis://:local@127.0.0.1:6379/0' JWT_SECRET='…' uv run pytest -v
  ```
- **Backend via Docker:** `docker compose … exec server` uses the production image (no `pytest`/`ruff` in PATH). Prefer host `uv` for backend checks.
- **Frontend:** `cd client && npm run lint && npm run test && npm run build` (Node 24 recommended per CI; Node 22 works with engine warnings).

### Optional services

- `make dev` — adds nginx + client containers (port 80).
- `make dev-worker` / `make dev-bot` — Celery worker + beat (RabbitMQ) and Telegram bot (need tokens).
