# gLOrng — Developer Portfolio & Personal Platform

Minimal, monospace-styled developer portfolio built with FastAPI + Vue 3 + MongoDB + Redis, fully containerized with Docker. The same domain services power the public site, admin panel, Telegram todobot, and background workers.

## Quick start

```bash
cp .env.example .env
make dev-lite          # terminal 1: mongodb, redis, API, nginx
make dev-lite-client   # terminal 2: Vite on :3000
make db-init           # if migrate did not run on stack start
make seed              # admin user (set SEED_PASSWORD in .env)
```

Open [http://localhost](http://localhost) or [http://localhost:3000](http://localhost:3000). API docs (dev): [http://localhost:8000/api/docs](http://localhost:8000/api/docs).

## Documentation

| Resource | Link |
|----------|------|
| **Handbook (local)** | `make docs-dev` → [http://localhost:5173](http://localhost:5173) |
| **Handbook (GitHub)** | [docs/index.md](docs/index.md) |
| **API / Postman** | [docs/reference/postman.md](docs/reference/postman.md) |
| **Cursor / agents** | [AGENTS.md](AGENTS.md) |

Topics: [getting started](docs/guide/getting-started.md), [architecture](docs/guide/architecture.md), [development](docs/guide/development.md), [deployment](docs/operations/deployment.md), [API reference](docs/reference/api-tools.md), [Postman](docs/reference/postman.md), [configuration](docs/reference/configuration.md), [security](docs/reference/security.md).

## Tech stack

- **Backend**: FastAPI, Motor (MongoDB), SQLAlchemy (optional Postgres), Celery, RabbitMQ, Redis
- **Frontend**: Vue 3, Vite, TypeScript, Tailwind CSS, Pinia
- **Proxy**: Nginx
- **Tooling**: uv, Ruff, pytest, ESLint, Vitest, Playwright, Docker Compose

## Project structure

```
server/    FastAPI backend (:8000)
client/    Vue 3 frontend (:3000)
nginx/     Reverse proxy (:80)
docs/      VitePress handbook
```

## Common commands

| Command | Description |
|---------|-------------|
| `make dev-lite` + `make dev-lite-client` | Default dev workflow |
| `make prod` | Production stack |
| `make check` | CI-equivalent lint + tests + client build |
| `make docs-dev` / `make docs-build` | Documentation site |

See [Development](docs/guide/development.md) for all `make` targets.

## License

MIT
