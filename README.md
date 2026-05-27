# gLOrng — Developer Portfolio

Minimal, monospace-styled developer portfolio built with FastAPI + Vue 3 + PostgreSQL + Redis, fully containerized with Docker.

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

## Features

- JWT authentication with email verification and password reset
- Email-restricted registration (single admin user)
- Redis: token blacklist, response cache, rate limiting, task queue
- Plugin architecture for admin tools (auto-discovery)
- Admin tools: Weather, Calculator, URL Shortener
- Donations: Stripe Payment Link, crypto addresses, Telegram
- Structured JSON logging + Sentry error tracking
- Ruff linting with enforced type annotations

## Architecture

```
Browser → Nginx (:80)
  ├── /           → Vue client (:3000)
  ├── /api/*      → FastAPI (:8000) → PostgreSQL / Redis
  ├── /admin/*    → FastAPI (:8000)
  └── /s/:code    → FastAPI → redirect
```

## License

MIT
