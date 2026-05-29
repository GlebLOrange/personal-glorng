# gLOrng — Developer Portfolio & Personal Platform

Minimal, monospace-styled developer portfolio built with FastAPI + Vue 3 + PostgreSQL + Redis, fully containerized with Docker. The same domain services power the public site, admin panel, Telegram todobot, and background workers.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy (async), Alembic, ARQ, Redis, Sentry
- **Frontend**: Vue 3, Vite, TypeScript, Tailwind CSS, SASS, Pinia
- **Database**: PostgreSQL 18
- **Cache/Queue**: Redis 8
- **Proxy**: Nginx
- **Tooling**: Ruff (lint/format), pytest, Docker Compose

## Quick Start

```bash
# Copy env file and edit values
cp .env.example .env

# Recommended for daily work (3 containers + Vite on host — lowest RAM)
make dev-lite
cd client && VITE_API_PROXY_TARGET=http://127.0.0.1:8000 npm run dev

# Or: full UI through nginx without worker/bot (5 containers)
make dev

# Run migrations (or rely on migrate service on `make dev`)
make db-init

# Seed admin user (after server is up)
make seed
```

Open [http://localhost:3000](http://localhost:3000) in lite mode, or [http://localhost](http://localhost) with `make dev`.

### Dev modes

| Command | Containers | Use when |
|---------|------------|----------|
| `make dev-lite` + host `npm run dev` | db, redis, server | Daily UI/API work (lowest resource use) |
| `make dev` | + client, nginx | Full stack through nginx; no background jobs |
| `make dev-worker` | + ARQ worker | Testing reminders, calendar sync, email jobs |
| `make dev-bot` | + Telegram todobot | Bot development (`TELEGRAM_BOT_TO_DO_TOKEN` required) |
| `make dev-full` | All 7 | Same as old default — worker + bot + nginx stack |

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
| Worker | `python -m app.workers.run` | Reminders, calendar sync, cleanup |
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
| `make dev-lite`    | Minimal stack (db, redis, API); run Vite on host |
| `make dev`         | Core dev stack (nginx + client; no worker/bot)   |
| `make dev-worker`  | Core stack + ARQ worker                          |
| `make dev-bot`     | Core stack + Telegram todobot                    |
| `make dev-full`    | All dev services (worker + bot)                  |
| `make prod`        | Start production environment                     |
| `make down`    | Stop all containers                  |
| `make test`    | Run backend tests                    |
| `make lint`    | Lint and format Python code          |
| `make db-init` | Run Alembic migrations (`migrate` service) |
| `make migrate` | Alias for `db-init`                  |
| `make db-reset`| Wipe DB volume and re-migrate (destructive) |
| `make seed`    | Create admin user                    |
| `make logs`    | Tail container logs                  |

## Platform Services

Admin tools are grouped into platform pillars:

| Pillar | Services |
|--------|----------|
| **Productivity** | Tasks, Email, Expenses |
| **Content** | Recipes, File share, URL shortener |
| **Utilities** | Calculator, Video download, AI chat |
| **Operations** | Feedback, Audit log |

Each capability follows a module-as-service pattern: business logic in `server/app/services/`, thin HTTP routers in `server/app/routers/tools/`, and a shared registry at `GET /api/platform/services`.

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

See [docs/platform.md](docs/platform.md) for the service catalog and audit model. Database setup and migrations: [docs/database.md](docs/database.md).

## License

MIT
