# Development

Day-to-day workflow, dev modes, ports, and quality checks.

## Recommended workflow

```bash
make                   # or: make dev — mongodb, redis, API, nginx (lite default)
make dev-lite-client   # terminal 2: Vite (:3000)
```

`make` / `make dev` alone does **not** start Vite — [http://localhost:3000](http://localhost:3000) will refuse connections until `make dev-lite-client` runs. RabbitMQ and the Docker Vite client stay off.

Daily `make` reuses the existing server image (app code is bind-mounted). Run `make rebuild` after `server/Dockerfile` or `server/uv.lock` changes.

If `npm run dev` fails with a missing `@rolldown/binding-*` module (common when `client/node_modules` was installed inside a Linux devcontainer), run `npm install` in `client/` on your host OS and retry.

## Dev modes

| Command | Containers / process | Use when |
|---------|----------------------|----------|
| `make` / `make dev` + `make dev-lite-client` | mongodb, redis, redis-cache, server, nginx + host Vite | **Default** daily workflow |
| `make dev-lite` | Alias for `make dev` | Same as default |
| `make dev-docker` | + Vite **client** container (profile `docker-client`) | All-in-Docker frontend |
| `make dev-ultra-lite-infra` + `make dev-ultra-lite-server` | mongodb, redis + host API | Debugging API on host; inline Celery |
| `make dev-search` | + elasticsearch | Elasticsearch-backed search |
| `make dev-postgres` | + postgres profile | Postgres FTS + audit secondary |
| `make dev-worker` | worker + beat + **broker** (RabbitMQ) | Real Celery jobs — set `CELERY_TASK_ALWAYS_EAGER=false` in `.env` or scheduled/async jobs stay inline on the API process |
| `make dev-bot` | bot + broker | Telegram todobot development |
| `make dev-full` | worker + bot + broker + docker-client | Everything in Docker |

Leave `ELASTICSEARCH_URL` empty for lite. MongoDB text search and optional Postgres FTS cover search without Elasticsearch. Default `.env.example` sets `CELERY_TASK_ALWAYS_EAGER=true` so on-demand Celery jobs (emails, reminders) run inline when dispatched. Calendar sync drain after enqueue / Retry / Sync now runs **in-process** via `process_sync_queue` (no worker required). Periodic beat schedules still need `make dev-worker` when `CELERY_TASK_ALWAYS_EAGER=false`. For real queues and beat, run `make dev-worker` and set `CELERY_TASK_ALWAYS_EAGER=false`.

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
| `make rebuild` | Rebuild images then start lite stack (after Dockerfile / lockfile changes) |
| `make db-init` / `make migrate` | Run migrations |
| `make seed-db` | Create admin + fixed-volume mock test data |
| `make reindex-search` | Rebuild search index |
| `make test` | Backend tests in Docker |
| `make lint` / `make lint-check` | Ruff (fix / check-only) |
| `make check` | Local backend lint + tests + client lint/test/build (not full CI) |
| `make logs` | Tail container logs |
| `make down` | Stop containers |

Full list: run `make` or see the [Makefile](../../Makefile).

## Logging (development)

Local defaults are quiet: `LOG_REQUESTS=false`, `APP_LOG_PERSIST_MIN_LEVEL=WARNING`, and uvicorn `--no-access-log`. You still get warnings/errors and intentional lifecycle logs (DB connect, auth events). Set `LOG_REQUESTS=true` in `.env` only when debugging HTTP. Production keeps request logging on — see [Configuration](/reference/configuration).

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
npm ci               # TypeScript ~5.9.x (typescript-eslint 8 peer range)
npm run dev          # dev server
npm run lint
npm run test
# Production build needs a public HTTPS origin (not localhost):
VITE_PUBLIC_ORIGIN=https://your-domain.example npm run build:check
```

Host Vite uses `client/.env.development` (`VITE_API_PROXY_TARGET=http://127.0.0.1:8000` by default) and also applies `VITE_*` from repo-root `.env`.

### Public route loading (perf / Lighthouse)

| Route | Without API | Notes |
|-------|-------------|--------|
| `/` (portfolio) | Renders from `RESUME_FALLBACK` immediately | Live `/resume` sync is non-blocking; failed sync shows a banner |
| `/news` | List skeleton until `loadNews()` resolves | Needs the API for article rows |

Do not treat a blank Lighthouse FCP on `vite preview` as “portfolio waits on the API” — check entry JS/CSS first (`npm run build:check` includes a no-chart-on-entry preload guard).

## Telegram todobot

With `make dev-bot` and `TELEGRAM_BOT_TO_DO_TOKEN` set:

| Command | Example |
|---------|---------|
| `/new` | Quick-create a task (also menu Quick / Guided) |
| `/tasks` | List pending tasks |
| `/connect_calendar` | Link Google Calendar |
| `/spend <text>` | `/spend 89.50 biedronka` |
| `/spend` | Guided expense flow |
| `/expenses` | This month's total and recent entries |

Default currency: `EXPENSE_DEFAULT_CURRENCY=PLN`.

How tasks, Telegram reminders, and Google Calendar sync connect: [Telegram + tasks + calendar sync](/guide/telegram-tasks-calendar).

**2026-09-23 — Google Keep:** `notes.create` is Workspace-only; a personal Gmail account cannot create Keep notes via API. A Create menu (Note vs Event; one Telegram message → Keep note, no task/calendar) was designed but is not in this tree. Do not plan Keep again unless the operator has Workspace.

## Quality checks

```bash
make lint-check
cd client && npm ci && npm run lint && npm run format:check
VITE_PUBLIC_ORIGIN=https://your-domain.example npm run build:check
make check   # local backend + frontend gate (CI also: coverage, postgres, e2e, docs)
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
