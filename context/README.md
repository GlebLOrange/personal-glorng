# Current Project Snapshot

**gLOrng** is a developer portfolio and personal platform. This page captures
the checked project state; update it whenever the runtime, dependency, or
development workflow changes.

## Stack

- **Backend:** FastAPI on Python 3.14, managed with `uv`.
- **Frontend:** Vue 3, Vite 8, and TypeScript 7.
- **Core data:** MongoDB is the primary datastore; Redis supports application
  state and a separate Redis instance is used as the cache.
- **Optional data and search:** PostgreSQL provides secondary audit storage and
  full-text search; Elasticsearch is an optional search backend.
- **Async services:** Celery with RabbitMQ powers background workers and beat;
  the Telegram todobot is available when its service and configuration are
  enabled.

## Default Development Workflow

Run these in separate terminals:

```bash
make dev
make dev-lite-client
```

`make dev` starts MongoDB, Redis, Redis cache, the FastAPI server, and nginx.
`make dev-lite-client` runs Vite on the host. In Lite mode nginx proxies the
frontend to host Vite, while RabbitMQ and the Docker client container stay off.

## Development Modes

| Command | Use case |
|---|---|
| `make dev` + `make dev-lite-client` | Default Lite workflow: Docker API/infrastructure plus host Vite. |
| `make dev-ultra-lite-infra` + `make dev-ultra-lite-server` | Run only MongoDB and Redis services in Docker; run the API on the host. |
| `make dev-docker` | Run the frontend in a Docker Vite client container. |
| `make dev-search` | Add Elasticsearch-backed search. |
| `make dev-postgres` | Add PostgreSQL for secondary search and audit storage. |
| `make dev-worker` | Start Celery worker and beat with RabbitMQ; set `CELERY_TASK_ALWAYS_EAGER=false` for queued jobs. |
| `make dev-bot` | Start the Telegram todobot with RabbitMQ. |
| `make dev-full` | Run worker, bot, RabbitMQ, and Docker frontend together. |

## Source of Truth

Use the [Makefile](../Makefile) for supported workflows, runtime commands, and
service composition. Confirm versions and dependency changes in
[client/package.json](../client/package.json) and
[server/pyproject.toml](../server/pyproject.toml); check
[Docker Compose files](../docker-compose.yml) for service topology and
[.env.example](../.env.example) for configuration requirements.

For historical architecture notes, see the dated
[project review](project-review.md) (2026-08-09).
