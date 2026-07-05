# Development

Day-to-day workflow, dev modes, ports, and quality checks.

## Recommended workflow

```bash
make dev-lite          # terminal 1: mongodb, redis, rabbitmq, API (:8000), nginx (:80)
make dev-lite-client   # terminal 2: Vite (:3000)
```

`make dev-lite` alone does **not** start Vite — [http://localhost:3000](http://localhost:3000) will refuse connections until `make dev-lite-client` runs.

If `npm run dev` fails with a missing `@rolldown/binding-*` module (common when `client/node_modules` was installed inside a Linux devcontainer), run `npm install` in `client/` on your host OS and retry.

## Dev modes

| Command | Containers / process | Use when |
|---------|----------------------|----------|
| `make dev-lite` + `make dev-lite-client` | mongodb, redis, rabbitmq, server, nginx + host Vite | **Default** daily workflow |
| `make dev` | + client container, nginx | Full stack in Docker; no worker/bot |
| `make dev-ultra-lite-infra` + `make dev-ultra-lite-server` | mongodb, redis + host API | Debugging API on host; inline Celery (no RabbitMQ) |
| `make dev-search` | + elasticsearch | Elasticsearch-backed search |
| `make dev-postgres` | + postgres profile | Postgres FTS + audit secondary |
| `make dev-worker` | worker + beat profiles | Real Celery jobs (RabbitMQ) |
| `make dev-bot` | bot profile | Telegram todobot development |
| `make dev-full` | worker + bot profiles | Everything |

Leave `ELASTICSEARCH_URL` empty for dev-lite. MongoDB text search and optional Postgres FTS cover search without Elasticsearch.

## Services and ports

| Service | URL / port |
|---------|------------|
| API (lite) | http://127.0.0.1:8000 — docs at `/api/docs` |
| Vite (host) | http://localhost:3000 |
| Nginx (lite) | http://localhost |
| MongoDB (host tools) | `127.0.0.1:27017` |
| Redis (host tools, ultra-lite) | `127.0.0.1:6379` |
| PostgreSQL (optional) | `127.0.0.1:5433` with `--profile postgres` |

## Make targets (common)

| Command | Description |
|---------|-------------|
| `make db-init` / `make migrate` | Run migrations |
| `make seed` | Create admin + sample data |
| `make reindex-search` | Rebuild search index |
| `make test` | Backend tests in Docker |
| `make lint` / `make lint-check` | Ruff (fix / check-only) |
| `make check` | Backend lint + tests + client lint/test/build |
| `make logs` | Tail container logs |
| `make down` | Stop containers |

Full list: run `make` or see the [Makefile](../../Makefile).

## Backend on the host

With [uv](https://docs.astral.sh/uv/) installed:

```bash
cd server
uv sync
uv run ruff check .
uv run pytest -v
```

Locked dependencies: `server/uv.lock`. Docker and CI use `uv sync --frozen`.

CI-style isolated venv (when Docker mounts `server/.venv`):

```bash
export PATH="$HOME/.local/bin:$PATH"
cd server
UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv sync --frozen
UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv run ruff check .
GLORNG_ENV_FILE=$PWD/tests/.env.test \
  UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv run pytest -v
```

## Frontend on the host

```bash
cd client
npm ci
npm run dev          # dev server
npm run lint
npm run test
npm run build:check  # typecheck + production build
```

Host Vite uses `client/.env.development` (`VITE_API_PROXY_TARGET=http://127.0.0.1:8000` by default).

## Telegram todobot

With `make dev-bot` and `TELEGRAM_BOT_TO_DO_TOKEN` set:

| Command | Example |
|---------|---------|
| `/spend <text>` | `/spend 89.50 biedronka` |
| `/spend` | Guided flow |
| `/expenses` | This month's total and recent entries |

Default currency: `EXPENSE_DEFAULT_CURRENCY=PLN`.

## Quality checks

```bash
make lint-check
cd client && npm ci && npm run lint && npm run format:check && npm run build:check
make check   # full CI-equivalent (backend + frontend)
```

E2E smoke (API on :8000):

```bash
cd client && npm run build:check && VITE_API_PROXY_TARGET=http://127.0.0.1:8000 npm run preview
# other terminal:
cd client && npm run e2e
```

Git hooks: `pip install pre-commit && pre-commit install`

Testing tiers and markers: [Testing](/reference/testing).

## Documentation site

```bash
make docs-dev    # VitePress at http://localhost:5173
make docs-build
```
