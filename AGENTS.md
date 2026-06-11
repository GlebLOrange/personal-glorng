# AGENTS.md

Coding standards and agent behavior live in [`.cursor/rules/`](.cursor/rules/) (stack conventions, git commit, PR workflow). Opt-in rules: `code-review-and-quality`, `incremental-implementation`, `test-driven-development`, `performance-optimization`, `security-and-hardening`, `frontend-ui-engineering`, `spec-driven-development`. This file covers environment and bootstrap only.

## Cursor Cloud specific instructions

### Product overview

**gLOrng** is a FastAPI + Vue 3 developer portfolio and personal platform. The recommended dev workflow is **ultra-lite mode**: MongoDB and Redis in Docker; API and Vite on the host. Use **lite mode** when you prefer the API in Docker.

### Cloud VM Docker caveat

Nested Docker on Cloud Agent VMs cannot apply Compose `deploy.resources` memory limits (cgroupv2 threaded mode). Always include the cloud overlay when starting services:

```bash
# Ultra-lite (lowest RAM): MongoDB + Redis only
docker compose -f docker-compose.yml -f docker-compose.ultra-lite.yml -f docker-compose.cloud-vm.yml up -d mongodb redis
make dev-ultra-lite-server

# Lite: API in Docker (also starts RabbitMQ via server depends_on)
docker compose -f docker-compose.yml -f docker-compose.lite.yml -f docker-compose.cloud-vm.yml up -d mongodb redis server
```

Equivalent to `make dev-ultra-lite-infra` / `make dev-lite` with the cloud overlay. Docker daemon on this VM also uses `fuse-overlayfs` and `default-cgroupns-mode: host` in `/etc/docker/daemon.json`.

For Elasticsearch-backed search, use `make dev-search` (add `-f docker-compose.search.yml` and `--profile search` to the compose command above) and set `ELASTICSEARCH_URL=http://elasticsearch:9200` in `.env`. Leave `ELASTICSEARCH_URL` empty for lite mode.

### First-time / manual setup

1. Copy env: `cp .env.example .env` and fill in all values (see `.env.example` for the full contract). Minimum secrets: `JWT_SECRET` (32+ chars), `REDIS_PASSWORD`, `MONGODB_PASSWORD`, and `SEED_PASSWORD`. Bootstrap knobs `RUN_MIGRATIONS` / `RUN_SEED` live in `.env` only—not Docker Compose overrides.
2. Start backend: `make dev-ultra-lite-infra` then `make dev-ultra-lite-server` (or lite/full compose commands above with the cloud overlay).
3. Seed admin: `cd server && GLORNG_ENV_FILE=../.env uv run python scripts/ensure_e2e_user.py` (or `make seed-ultra-lite` / `make seed` with `SEED_PASSWORD` set).
4. Backfill search index (first deploy or after schema changes): `make reindex-search`
5. Frontend: `cd client && VITE_API_PROXY_TARGET=http://127.0.0.1:8000 npm run dev` → http://localhost:3000

Default E2E credentials: `admin@admin.admin` / `MyTestPass123!`

### Services and ports

| Service | URL / port |
|---------|------------|
| API (ultra-lite / lite) | http://127.0.0.1:8000 — docs at `/api/docs` |
| Vite (host) | http://localhost:3000 |
| MongoDB (host tools) | `127.0.0.1:27017` |
| Redis (host tools, ultra-lite) | `127.0.0.1:6379` |
| PostgreSQL (optional secondary) | `127.0.0.1:5433` with `--profile postgres` |

### Lint / test / build

See `README.md` for canonical commands. **Agents skip test execution in dev by default** — see [`.cursor/rules/skip-tests-in-dev.mdc`](.cursor/rules/skip-tests-in-dev.mdc). CI runs the full suite on pull requests; use the commands below manually when you want local verification.

Cloud-specific notes:

- **Backend lint/tests (host, matches CI backend job):** use an isolated venv because Docker mounts `server/.venv`:
  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  cd server
  UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv sync --frozen
  UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv run ruff check .
  GLORNG_ENV_FILE=$PWD/tests/.env.test \
  UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv run pytest -v
  ```
- **Backend via Docker:** `docker compose … exec server` uses the production image (no `pytest`/`ruff` in PATH). Prefer host `uv` for backend checks.
- **Frontend:** `cd client && npm run lint && npm run test && npm run build:check` (Node 24 recommended per CI; Node 22 works with engine warnings). Use `npm run build` for a fast Vite-only bundle. Agents may run lint and build without test unless asked.

### Optional services

- `make dev-ultra-lite-infra` / `make dev-ultra-lite-server` — lowest RAM; host API with inline Celery (no RabbitMQ).
- `make dev-lite` — API in Docker; also starts RabbitMQ via `server` depends_on.
- `make dev` — adds nginx + client containers (port 80).
- `make dev-postgres` — adds Postgres for FTS search / audit secondary storage.
- `make dev-worker` / `make dev-bot` — Celery worker + beat (RabbitMQ) and Telegram bot (need tokens).
