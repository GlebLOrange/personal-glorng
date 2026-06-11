# gLOrng — Developer Portfolio & Personal Platform

Minimal, monospace-styled developer portfolio built with FastAPI + Vue 3 + MongoDB + Redis, fully containerized with Docker. The same domain services power the public site, admin panel, Telegram todobot, and background workers.

## Tech Stack

- **Backend**: FastAPI, Motor (MongoDB), SQLAlchemy (async, optional Postgres), Alembic, Celery, RabbitMQ, Redis, Sentry
- **Frontend**: Vue 3, Vite, TypeScript, Tailwind CSS, SASS, Pinia
- **Database**: MongoDB (primary); PostgreSQL 18 optional (`--profile postgres` for FTS search + audit)
- **Cache/Queue**: Redis 8
- **Proxy**: Nginx
- **Tooling**: uv (Python deps), Ruff (lint/format), pytest, ESLint, Prettier, Vitest, Playwright, Docker Compose

## Quick Start

```bash
# Copy env file and edit values
cp .env.example .env

# Recommended for daily work (2 Docker containers + host API + host Vite — lowest RAM)
make dev-ultra-lite-infra    # terminal 1: mongodb + redis
make dev-ultra-lite-server   # terminal 2: host uvicorn (:8000)
cd client && VITE_API_PROXY_TARGET=http://127.0.0.1:8000 npm run dev   # terminal 3: Vite (:3000)

# Or: API in Docker (also starts RabbitMQ via server depends_on)
make dev-lite                # terminal 1: mongodb, redis, rabbitmq, API (:8000)
cd client && VITE_API_PROXY_TARGET=http://127.0.0.1:8000 npm run dev   # terminal 2: Vite (:3000)

# Or: full UI through nginx without worker/bot (5 containers)
make dev

# Run migrations (or rely on migrate service on `make dev`)
make db-init

# Seed admin user (after server is up)
make seed
```

Open [http://localhost:3000](http://localhost:3000) in ultra-lite or lite mode, or [http://localhost](http://localhost) with `make dev`.

Ultra-lite and dev-lite start the **API only** in the first terminal. Without the `npm run dev` step, [http://localhost:3000](http://localhost:3000) will refuse connections even when the API on :8000 is healthy. If `npm run dev` fails with a missing `@rolldown/binding-*` module (common when `client/node_modules` was installed in a Linux devcontainer), run `npm install` in `client/` on your host OS and retry.

API docs (dev only): [http://localhost:8000/api/docs](http://localhost:8000/api/docs) with host or container API, or `/api/docs` through nginx with `make dev`. Authorize with Bearer token from `POST /api/auth/login`.

### Dev modes

| Command | Containers | Use when |
|---------|------------|----------|
| `make dev-ultra-lite-infra` + `make dev-ultra-lite-server` + host `npm run dev` | mongodb, redis only | Lowest RAM — host API + Vite; Celery runs inline (no RabbitMQ) |
| `make dev-lite` + host `npm run dev` | mongodb, redis, rabbitmq, server | API in Docker; also pulls RabbitMQ via `server` depends_on |
| `make dev-search` | mongodb, redis, elasticsearch, server | Elasticsearch-backed full-text search (`ELASTICSEARCH_URL` required) |
| `make dev` | + client, nginx | Full stack through nginx; no background jobs |
| `make dev-worker` | + Celery worker + beat + RabbitMQ | Testing reminders, calendar sync, email jobs |
| `make dev-bot` | + Telegram todobot | Bot development (`TELEGRAM_BOT_TO_DO_TOKEN` required) |
| `make dev-full` | All 7 | Same as old default — worker + bot + nginx stack |

Leave `ELASTICSEARCH_URL` empty in `.env` for ultra-lite and dev-lite (default). MongoDB text search and optional Postgres FTS cover search without Elasticsearch. Use `make dev-worker` when you need real async Celery jobs (RabbitMQ + worker + beat).

## Project Structure

```
server/    FastAPI backend (:8000)
client/    Vue 3 frontend (:3000)
nginx/     Reverse proxy config (:80)
```

## Runtime Entrypoints

| Process | Command | Role |
|---------|---------|------|
| API | `uvicorn app.main:app` | HTTP API, admin tools, public routes |
| Worker | `celery -A app.workers.celery_app worker` | Reminders, calendar sync, cleanup |
| Beat | `celery -A app.workers.celery_app beat` | Cron schedules for worker tasks |
| Todobot | `python -m app.todobot.main` | Telegram tasks + expense logging |

### Telegram expense logging

With `make dev-bot` and `TELEGRAM_BOT_TO_DO_TOKEN` set, log spending from the same todobot:

| Command | Example |
|---------|---------|
| `/spend <text>` | `/spend 89.50 biedronka` |
| `/spend` | Guided flow (amount → category → optional place) |
| `/expenses` | This month's total (PLN) and recent entries |

Default currency: `EXPENSE_DEFAULT_CURRENCY=PLN` in `.env`.

## Available Commands

| Command            | Description                                      |
|--------------------|--------------------------------------------------|
| `make dev-ultra-lite-infra` | MongoDB + Redis in Docker; runs migrate |
| `make dev-ultra-lite-server` | Host uvicorn (:8000); run after infra |
| `make dev-lite`    | Minimal stack (db, redis, API); run Vite on host |
| `make dev-search`  | Lite stack + Elasticsearch (set `ELASTICSEARCH_URL` in `.env`) |
| `make dev`         | Core dev stack (nginx + client; no worker/bot)   |
| `make dev-worker`  | Core stack + RabbitMQ + Celery worker + beat   |
| `make dev-bot`     | Core stack + Telegram todobot                    |
| `make dev-full`    | All dev services (worker + bot)                  |
| `make prod`        | Start production environment                     |
| `make down`    | Stop all containers                  |
| `make test`    | Run backend tests                    |
| `make lint`    | Lint and format Python code (auto-fix) |
| `make lint-check` | Ruff verify-only (matches CI)    |
| `make check`   | Backend lint-check + tests + optional db-check + client lint/test/build |
| `make db-check`| Alembic migration graph check        |
| `make db-init` | Run Alembic migrations (`migrate` service) |
| `make db-init-ultra-lite` | Run migrate service with ultra-lite compose files |
| `make migrate` | Alias for `db-init`                  |
| `make db-reset`| Wipe DB volume and re-migrate (destructive) |
| `make seed`    | Create admin user                    |
| `make seed-ultra-lite` | Create admin user (host uv, ultra-lite) |
| `make reindex-search` | Rebuild FTS search index from all sources |
| `make logs`    | Tail container logs                  |

## AI search deploy

After migrations on a fresh database, backfill the unified search index:

```bash
make db-init
make reindex-search
```

Resume content is upserted automatically on API startup when `AI_SEARCH_ENABLED=true`. Recipes, tasks, expenses, and other sources are indexed on create/update; run `make reindex-search` after deploy to backfill existing rows.

Set `AI_SEARCH_ENABLED`, `OPENAI_API_KEY`, and `VITE_AI_SEARCH_ENABLED` in `.env` (see `.env.example`).

## Platform Services

Admin tools are grouped into platform pillars:

| Pillar | Services |
|--------|----------|
| **Productivity** | Tasks, Email, Expenses |
| **Content** | Recipes, File share, URL shortener |
| **Utilities** | Calculator, Video download, AI chat |
| **Operations** | Feedback, Audit log |

Each capability follows a module-as-service pattern: business logic in `server/app/services/`, thin HTTP routers in `server/app/routers/tools/`, and a shared registry at `GET /api/platform/services`. See [docs/api-tools.md](docs/api-tools.md) for public vs admin endpoints and capability keys.

## Features

- JWT authentication with email verification and password reset
- Email-restricted registration (single admin user)
- Redis: token blacklist, response cache, rate limiting, task queue
- Plugin architecture for admin tools (auto-discovery)
- Telegram todobot: tasks, reminders, and quick expense logging (`/spend`, `/expenses`)
- Donations: Stripe Payment Link, crypto addresses, Telegram
- Two-stream observability: operational telemetry (JSON logs + Sentry) and persistent audit trail (`audit_events`)
- Ruff linting with enforced type annotations

## Architecture

```
Browser → Nginx (:80)
  ├── /              → Vue client (:3000)
  ├── /admin/*       → Vue client (admin SPA)
  ├── /api/*         → FastAPI (:8000) → PostgreSQL / Redis
  ├── /s/:code       → FastAPI → redirect
  └── /f/:code       → FastAPI → file download

FastAPI + Worker + Todobot share PostgreSQL and Redis
```

See [docs/platform.md](docs/platform.md) for the service catalog and audit model. API tool reference: [docs/api-tools.md](docs/api-tools.md). Database setup and migrations: [docs/database.md](docs/database.md). Security posture and hardening notes: [docs/security.md](docs/security.md).

## Backend development (host)

With [uv](https://docs.astral.sh/uv/) installed:

```bash
cd server
uv sync
uv run ruff check .
uv run pytest -v
```

Locked dependencies live in `server/uv.lock`; Docker and CI use `uv sync --frozen`.

## Quality checks

With `make dev-ultra-lite-server` or `make dev-lite` running (API up):

```bash
make lint-check && make test
cd client && npm ci && npm run lint && npm run format:check && npm run test && npm run build:check
```

Optional end-to-end smoke tests (API on :8000, then):

```bash
cd client && npm run build:check && VITE_API_PROXY_TARGET=http://127.0.0.1:8000 npm run preview
# other terminal:
cd client && npm run e2e
```

Install git hooks: `pip install pre-commit && pre-commit install` (ruff, client eslint/prettier/typecheck, gitleaks)

CI runs backend ruff/pytest, frontend lint/test/build, Alembic check, and Playwright smoke tests on pull requests (see `.github/workflows/ci.yml`).

## License

MIT
