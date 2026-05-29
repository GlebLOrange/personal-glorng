# gLOrng — Developer Portfolio & Personal Platform

Minimal, monospace-styled developer portfolio built with FastAPI + Vue 3 + PostgreSQL + Redis, fully containerized with Docker. The same domain services power the public site, admin panel, Telegram todobot, and background workers.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy (async), Alembic, ARQ, Redis, Sentry
- **Frontend**: Vue 3, Vite, TypeScript, Tailwind CSS, SASS, Pinia
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Proxy**: Nginx
- **Tooling**: Ruff (lint/format), pytest, Docker Compose

## Quick Start

```bash
# Copy env file and edit values
cp .env.example .env

# Start all services (dev)
make dev

# Run migrations
make migrate

# Seed admin user
make seed
```

Open [http://localhost](http://localhost) in your browser.

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
| Todobot | `python -m app.todobot.main` | Telegram task bot |

## Available Commands

| Command        | Description                          |
|----------------|--------------------------------------|
| `make dev`     | Start dev environment                |
| `make prod`    | Start production environment         |
| `make down`    | Stop all containers                  |
| `make test`    | Run backend tests                    |
| `make lint`    | Lint and format Python code          |
| `make migrate` | Run Alembic migrations               |
| `make seed`    | Create admin user                    |
| `make logs`    | Tail container logs                  |

## Platform Services

Admin tools are grouped into platform pillars:

| Pillar | Services |
|--------|----------|
| **Productivity** | Tasks, Email |
| **Content** | Recipes, File share, URL shortener |
| **Utilities** | Weather, Calculator, Video download, AI chat |
| **Operations** | Expenses, Feedback, Audit log |

Each capability follows a module-as-service pattern: business logic in `server/app/services/`, thin HTTP routers in `server/app/routers/tools/`, and a shared registry at `GET /api/platform/services`.

## Features

- JWT authentication with email verification and password reset
- Email-restricted registration (single admin user)
- Redis: token blacklist, response cache, rate limiting, task queue
- Plugin architecture for admin tools (auto-discovery)
- Telegram todobot sharing task services with admin and worker
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

See [docs/platform.md](docs/platform.md) for the service catalog and audit model.

## License

MIT
