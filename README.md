# gLOrng — Developer Portfolio & Personal Platform

Minimal, monospace-styled developer portfolio built with FastAPI + Vue 3 + MongoDB + Redis, fully containerized with Docker. The same domain services power the public site, admin panel, Telegram todobot, and background workers.

## Tech Stack

- **Backend**: FastAPI, Motor (MongoDB), SQLAlchemy (async, optional Postgres), Alembic, Celery, RabbitMQ, Redis, Sentry
- **Frontend**: Vue 3, Vite, TypeScript, Tailwind CSS, Pinia
- **Database**: MongoDB (primary); PostgreSQL 18 optional (`--profile postgres` for FTS search + audit)
- **Cache/Queue**: Redis 8
- **Proxy**: Nginx
- **Tooling**: uv (Python deps), Ruff (lint/format), pytest, ESLint, Prettier, Vitest, Playwright, Docker Compose

## Quick Start

```bash
# Copy env file and edit values
cp .env.example .env

# Recommended for daily work: API in Docker, Vite on the host
make dev-lite                # terminal 1: mongodb, redis, rabbitmq, API (:8000), nginx (:80)
make dev-lite-client         # terminal 2: Vite (:3000) - open http://localhost or :3000

# Or: full UI through nginx without worker/bot (5 containers)
make dev

# Run migrations (or rely on migrate service on `make dev`)
make db-init

# Seed admin user (after server is up)
make seed
```

Open [http://localhost](http://localhost) with `make dev-lite` + `make dev-lite-client`, or [http://localhost:3000](http://localhost:3000) if you skip nginx. `make dev` also serves [http://localhost](http://localhost).

`make dev-lite` starts the API and nginx in the first terminal. Without the `npm run dev` step, [http://localhost:3000](http://localhost:3000) will refuse connections even when the API on :8000 is healthy. If `npm run dev` fails with a missing `@rolldown/binding-*` module (common when `client/node_modules` was installed in a Linux devcontainer), run `npm install` in `client/` on your host OS and retry.

API docs (dev only): [http://localhost:8000/api/docs](http://localhost:8000/api/docs) with host or container API, or `/api/docs` through nginx with `make dev`. Authorize with Bearer token from `POST /api/auth/login`.

### Dev modes

| Command | Containers | Use when |
|---------|------------|----------|
| `make dev-lite` + `make dev-lite-client` | mongodb, redis, rabbitmq, server, nginx | Default daily workflow; API in Docker, Vite on the host |
| `make dev` | + client, nginx | Full stack through nginx; no background jobs |

Advanced dev modes remain available when you need them: `make dev-ultra-lite-infra` + `make dev-ultra-lite-server` for host API work, `make dev-search` for Elasticsearch, `make dev-worker` for real Celery jobs, `make dev-bot` for Telegram bot development, and `make dev-full` for everything.

Leave `ELASTICSEARCH_URL` empty in `.env` for dev-lite (default). MongoDB text search and optional Postgres FTS cover search without Elasticsearch.

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
| `make dev-lite`    | Default dev stack (MongoDB, Redis, API, nginx); pair with `make dev-lite-client` |
| `make dev-lite-client` | Host Vite on :3000 (uses `client/.env.development`) |
| `make dev`         | Core dev stack (nginx + client; no worker/bot)   |
| `make prod`        | Start production environment                     |
| `make prod-cloudflare` | Start production with nginx origin TLS for Cloudflare Full strict |
| `make down`    | Stop all containers                  |
| `make test`    | Run backend tests                    |
| `make lint`    | Lint and format Python code (auto-fix) |
| `make lint-check` | Ruff verify-only (matches CI)    |
| `make check`   | Backend lint-check + tests + optional db-check + client lint/test/build |
| `make db-check`| Alembic migration graph check        |
| `make db-init` | Run Alembic migrations (`migrate` service) |
| `make migrate` | Alias for `db-init`                  |
| `make db-reset`| Wipe DB volume and re-migrate (destructive) |
| `make seed`    | Create admin user                    |
| `make reindex-search` | Rebuild FTS search index from all sources |
| `make logs`    | Tail container logs                  |

## AI search deploy

After migrations on a fresh database, backfill the unified search index:

```bash
make db-init
make reindex-search
```

Public resume content is defined in `server/app/content/resume_data.py`, mirrored in `client/src/constants/resumeFallback.ts` for offline rendering, and exposed at `GET /api/resume`. Resume chunks are upserted automatically on API startup when `AI_SEARCH_ENABLED=true`. Recipes, tasks, expenses, and other sources are indexed on create/update; run `make reindex-search` after deploy to backfill existing rows.

Set `AI_SEARCH_ENABLED`, `GEMINI_API_KEY`, and `VITE_AI_SEARCH_ENABLED` in `.env` (see `.env.example`).

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
- Module-as-service architecture for admin tools
- Telegram todobot: tasks, reminders, and quick expense logging (`/spend`, `/expenses`)
- Donations: Stripe card checkout, PayPal, Patreon
- Two-stream observability: operational telemetry (JSON logs + Sentry) and persistent audit trail (`audit_events`)
- Ruff linting with enforced type annotations

## Architecture

```
Browser → Nginx (:80)
  ├── /              → Vue client (:3000)
  ├── /admin/*       → Vue client (admin SPA)
  ├── /api/*         → FastAPI (:8000) → MongoDB / Redis
  ├── /s/:code       → FastAPI → redirect
  └── /f/:code       → FastAPI → file download

FastAPI + Worker + Todobot share MongoDB and Redis.
PostgreSQL is optional for secondary FTS search and audit storage.
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

Non-test checks for local production-readiness review:

```bash
make lint-check
cd client && npm ci && npm run lint && npm run format:check && npm run build:check
```

Full CI-equivalent checks also run backend/frontend tests and Playwright smoke tests:

```bash
make check
cd client && npm run e2e
```

Bundle size report (writes `client/dist/stats.html`):

```bash
cd client && npm run analyze
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
