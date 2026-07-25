# AGENTS.md

Coding standards and agent behavior use a hybrid layout: thin always-on and path-triggered stubs in [`.cursor/rules/`](.cursor/rules/) (safety, git workflow, dependencies, backend FastAPI/Python, frontend Vue/Pinia/TypeScript, design system) that point at full guidance in [`.cursor/skills/`](.cursor/skills/), plus opt-in review/process skills such as `code-review-and-quality`, `incremental-implementation`, `test-driven-development`, `performance-optimization`, `security-and-hardening`, and `spec-driven-development`. This file covers environment and bootstrap only. Ecosystem skills from skills.sh: install with `npx skills add <pkg>@<skill> -g -y` (user-level under `~/.agents/skills/`); keep project skills in `.cursor/skills/` only — do not commit `.agents/`, `.claude/`, or `skills-lock.json`.

## Cursor Cloud specific instructions

### Product overview

**gLOrng** is a FastAPI + Vue 3 developer portfolio and personal platform. The default dev workflow is **lite mode** (`make` / `make dev`): MongoDB, Redis, API, and nginx in Docker; Vite on the host with `make dev-lite-client`. RabbitMQ and the Vite client container stay off until you opt in.

### Cloud VM Docker caveat

Nested Docker on Cloud Agent VMs cannot apply Compose `deploy.resources` memory limits (cgroupv2 threaded mode). Always include the cloud overlay when starting services:

```bash
# Lite: API in Docker (no RabbitMQ / client container)
docker compose -f docker-compose.yml -f docker-compose.lite.yml -f docker-compose.cloud-vm.yml up -d mongodb redis redis-cache server nginx

# Ultra-lite, when you specifically want host API work
docker compose -f docker-compose.yml -f docker-compose.ultra-lite.yml -f docker-compose.cloud-vm.yml up -d mongodb redis
make dev-ultra-lite-server
```

Equivalent to `make dev-lite` / `make dev-ultra-lite-infra` with the cloud overlay. Docker daemon on this VM uses `fuse-overlayfs` and `default-cgroupns-mode: host` in `/etc/docker/daemon.json`. On Docker 29+ the daemon.json must also set `"features": {"containerd-snapshotter": false}`, otherwise `fuse-overlayfs` is ignored. The `docker-compose.cloud-vm.yml` overlay must reset `deploy` (memory limits) and set `cgroup: host` for **every** service you start — including `mongodb` and `rabbitmq`; without that reset those containers fail with `cannot enter cgroupv2 ... it is in threaded mode`.

The Docker daemon is not auto-started on a fresh VM. Start it once per session before running compose: `sudo dockerd > /tmp/dockerd.log 2>&1 &` (wait for `docker info` to succeed).

For Elasticsearch-backed search, use `make dev-search` (add `-f docker-compose.search.yml` and `--profile search` to the compose command above) and set `ELASTICSEARCH_URL=http://elasticsearch:9200` in `.env`. Leave `ELASTICSEARCH_URL` empty for lite mode.

### First-time / manual setup

1. Copy env: `cp .env.example .env` and fill in all values (see `.env.example` for the full contract). Minimum secrets: `JWT_SECRET` (32+ chars), `REDIS_PASSWORD`, `MONGODB_PASSWORD`, and `SEED_PASSWORD`. Bootstrap knobs `RUN_MIGRATIONS` / `RUN_SEED` live in `.env` only—not Docker Compose overrides. **`SEED_PASSWORD` must satisfy the login password policy** (12+ chars with upper, lower, digit, and special char, e.g. `MyTestPass123!`) — the `.env.example` default `password_seed` seeds an admin that then cannot log in (the login schema rejects it). `seed_admin` skips existing users, so if you seeded with a bad password, recreate the DB (`docker compose ... down -v` then up) after fixing `SEED_PASSWORD`.
2. Start backend: `make dev-lite` (or the lite compose command above with the cloud overlay).
3. Seed admin: `make seed` with `SEED_PASSWORD` set.
4. Backfill search index (first deploy or after schema changes): `make reindex-search`
5. Frontend: `make dev-lite-client` → http://localhost (dev-lite nginx) or http://localhost:3000

Default E2E credentials: `admin@admin.admin` / `MyTestPass123!`

### Services and ports

| Service | URL / port |
|---------|------------|
| API (lite) | http://127.0.0.1:8000 — docs at `/api/docs` |
| Vite (host) | http://localhost:3000 |
| MongoDB (host tools) | `127.0.0.1:27017` |
| Redis (host tools, ultra-lite only) | `127.0.0.1:6379` |
| PostgreSQL (optional secondary) | `127.0.0.1:5433` with `--profile postgres` |

### Lint / test / build

See `README.md` for canonical commands. Agents prefer targeted checks in dev by default; CI runs the full suite on pull requests. Use the commands below manually when you want local full-suite verification.

Docs: published handbook at https://gleblorange.github.io/portfolio-glorng/ ; regenerate OpenAPI/inventory with `make docs-generate` after router or registry changes.

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
- **Backend via Docker:** prod images do not include `pytest`/`ruff`; dev targets may, but host `uv` is the canonical path for backend checks.
- **Frontend:** Node 24 (`engines` + root `.nvmrc`; Cloud VM default `/exec-daemon/node` is often v22 — prepend `"$HOME/.nvm/versions/node/v24.18.0/bin"` to `PATH` or `nvm use`). From `client/`: `npm ci`, then `npm run lint && npm run format:check && npm run test:coverage && npm run build:check`. Use `npm run build` for a fast Vite-only bundle. TypeScript is pinned to `~5.8.3` so `typescript-eslint@8` peers resolve; do not bump to TS 7 until the ESLint stack supports it.

### Optional services

- `make` / `make dev` — lite default: mongodb, redis, redis-cache, server, nginx (no RabbitMQ / client container).
- `make dev-lite` — alias for `make dev`.
- `make dev-docker` — Vite client container + nginx (profile `docker-client`).
- `make dev-ultra-lite-infra` / `make dev-ultra-lite-server` — host API with inline Celery (no RabbitMQ).
- `make dev-postgres` — adds Postgres for FTS search / audit secondary storage.
- `make dev-worker` / `make dev-bot` — Celery worker + beat and Telegram bot; enable RabbitMQ via profile `broker` (set `CELERY_TASK_ALWAYS_EAGER=false`).
