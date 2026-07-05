# Getting started

Minimal setup for local development with the recommended **lite mode**: API in Docker, Vite on the host.

## Prerequisites

- Docker and Docker Compose
- Node.js 22+ (24 recommended per CI)
- [uv](https://docs.astral.sh/uv/) for host-side backend work (optional)

## First-time setup

```bash
cp .env.example .env
# Edit .env — minimum secrets below

make dev-lite          # terminal 1: mongodb, redis, API, nginx
make dev-lite-client   # terminal 2: Vite on :3000
make db-init           # if migrate did not run on stack start
make seed              # admin user (needs SEED_PASSWORD in .env)
```

Open [http://localhost](http://localhost) (nginx + Vite) or [http://localhost:3000](http://localhost:3000).

API docs (dev only): [http://localhost:8000/api/docs](http://localhost:8000/api/docs). Authorize with a Bearer token from `POST /api/auth/login`.

## Minimum `.env` secrets

| Variable | Requirement |
|----------|-------------|
| `JWT_SECRET` | 32+ random characters |
| `REDIS_PASSWORD` | Strong password |
| `MONGODB_PASSWORD` | Strong password |
| `SEED_PASSWORD` | Password for bootstrap admin |

Bootstrap knobs `RUN_MIGRATIONS` and `RUN_SEED` live in `.env` only — not Docker Compose overrides.

Default E2E credentials after seed: `admin@admin.admin` / value of `SEED_PASSWORD` (see `E2E_PASSWORD` in `.env.example`).

## AI search (optional)

After a fresh database:

```bash
make db-init
make reindex-search
```

Set `AI_SEARCH_ENABLED`, `GEMINI_API_KEY`, and `VITE_AI_SEARCH_ENABLED` in `.env`. Full variable reference: [Configuration](/reference/configuration).

## Next steps

- [Development modes](/guide/development) — all `make dev-*` targets
- [Architecture](/guide/architecture) — how requests and services fit together
- [Deployment](/operations/deployment) — production checklist
