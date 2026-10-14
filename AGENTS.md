# AGENTS.md

## Where guidance lives

- **Coding standards:** [`CODING_STANDARDS.md`](CODING_STANDARDS.md) — language, style, lint policy, dependencies, and design system (links into [`.cursor/skills/`](.cursor/skills/); path-triggered [`.cursor/rules/`](.cursor/rules/) stubs load those skills).
- **This file:** Environment, bootstrap, and **Cursor Cloud VM** operational caveats — always injected; see [Cursor Cloud VM — Docker caveats](#cursor-cloud-vm--docker-caveats) and [Cloud VM lint / test / build](#cloud-vm-lint--test--build).
- **Handbook:** https://gleblorange.github.io/personal-glorng/ — human-oriented docs. Step-by-step first-time setup: [`docs/guide/getting-started.md`](docs/guide/getting-started.md).

Do not commit ephemeral PR review dumps at the repo root (that anti-pattern lived as `BASEDIR.md`). Generic process skills (TDD, code-review, security hardening, etc.) live user-level under `~/.cursor/skills` / `~/.agents/skills` — install with `npx skills add <pkg>@<skill> -g -y`; keep project skills in `.cursor/skills/` only — do not commit `.agents/`, `.claude/`, or `skills-lock.json`.

## Product and default dev

**Gleb.Y** is a FastAPI + Vue 3 developer portfolio and personal platform.

Default dev is **lite mode**: MongoDB, Redis, API, and nginx in Docker; Vite on the host with `make dev-lite-client`. RabbitMQ and the Vite client container stay off until you opt in ([Optional services](#optional-services)).

## Cursor Cloud VM — Docker caveats

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

## Agent setup traps

Full bootstrap (env, stack, seed, search index, frontend URLs): follow [Getting started](docs/guide/getting-started.md).

Keep these agent-specific traps in mind:

- **`SEED_PASSWORD` must satisfy the login password policy** (12+ chars with upper, lower, digit, and special char, e.g. `MyTestPass123!`). The `.env.example` default `password_seed` seeds an admin that then **cannot log in** (the login schema rejects it).
- **`seed_admin` skips existing users** — if you seeded with a bad password, fix `SEED_PASSWORD` and **recreate the DB** (`docker compose ... down -v` then up) before re-seeding.
- Bootstrap knobs `RUN_MIGRATIONS` / `RUN_SEED` live in **`.env` only** — not Docker Compose overrides.
- On **Cursor Cloud VM**, start the backend with the [cloud overlay compose commands](#cursor-cloud-vm--docker-caveats) (not bare `make dev-lite` alone).

Default E2E credentials: `admin@admin.admin` / `MyTestPass123!`

## Services and ports

| Service | URL / port |
|---------|------------|
| API (lite) | http://127.0.0.1:8000 — docs at `/api/docs` |
| Vite (host) | http://localhost:3000 |
| MongoDB (host tools) | `127.0.0.1:27017` |
| Redis (host tools, ultra-lite only) | `127.0.0.1:6379` |
| PostgreSQL (optional secondary) | `127.0.0.1:5433` with `--profile postgres` |

## Cloud VM lint / test / build

Agents prefer targeted checks in dev; CI runs the full suite on pull requests. README lists the full command matrix — use the commands below on Cursor Cloud VM for host-side full-suite checks.

Regenerate OpenAPI/inventory with `make docs-generate` after router or registry changes.

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
- **Frontend:** Node 24 (`engines` + root `.nvmrc`; Cloud VM default `/exec-daemon/node` is often v22 — prepend `"$HOME/.nvm/versions/node/v24.18.0/bin"` to `PATH` or `nvm use`). From `client/`: `npm ci`, then `npm run lint && npm run format:check && npm run test:coverage`. For `npm run build:check`, set `VITE_PUBLIC_ORIGIN` to a public HTTPS origin (CI uses `https://ci.example.test`; prod uses your `BASE_URL`). Use `npm run build` only for a fast local bundle without the OG origin guard. TypeScript is pinned to `~5.9.3` (see `client/package.json`).

## Optional services

- **`make` / `make dev` / `make dev-lite`** — same lite stack: mongodb, redis, redis-cache, server, nginx (no RabbitMQ / client container).
- `make dev-docker` — Vite client container + nginx (profile `docker-client`).
- `make dev-ultra-lite-infra` / `make dev-ultra-lite-server` — host API with inline Celery (no RabbitMQ).
- `make dev-postgres` — adds Postgres for FTS search / audit secondary storage.
- `make dev-worker` / `make dev-bot` — Celery worker + beat and Telegram bot; enable RabbitMQ via profile `broker` (set `CELERY_TASK_ALWAYS_EAGER=false`).
