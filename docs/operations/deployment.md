# Deployment

Production runbook for starting and operating the Docker Compose stack ([`docker-compose.prod.yml`](../../docker-compose.prod.yml)).

## Navigation

1. [Prerequisites](#1-prerequisites) — Docker, ports, repo checkout
2. [Env file](#2-env-file) — `.env` from the production template
3. [Start stack](#3-start-stack) — `make prod` / `make prod-cloudflare`
4. [First-boot extras](#4-first-boot-extras) — seed admin, reindex search
5. [Verify](#5-verify) — `ps`, health, ready
6. [Day-2 ops](#6-day-2-ops) — logs, stop, rebuild (prod compose file)
7. [Optional add-ons](#7-optional-add-ons) — Postgres, AI search, Cloudflare

Later: [Sentry releases](#sentry-releases-optional-ci) · [Staging checks](#staging-manual-checks-p3) · [Celery DLQ](#celery-dead-letter-queue)

GitHub / CI gates (development vs production): [DevOps checklist](/operations/devops-checklist#development-vs-production-github--cicd).

---

## 1. Prerequisites

**Why:** Prod expects Docker Compose on the host and free publish ports before anything starts.

- Docker Engine + Compose v2 on the deploy host
- Repo checkout at the revision you want to run
- Port **80** free (nginx). Port **443** free only if you use Cloudflare origin TLS
- Prod compose enables log rotation (`10m` × 3), `no-new-privileges`, and `init` on services

Compose service inventory: [architecture inventory (generated)](/generated/architecture-inventory).

## 2. Env file

**Why:** Containers mount `./.env` read-only; startup validates production secrets before the API stays up.

1. Copy [`.env.production.example`](../../.env.production.example) (or `.env.example`) to `.env` and fill blanks.
2. Set `APP_ENV=production`.
3. Strong secrets (validated at startup):
   - `JWT_SECRET` — 32+ chars, no weak markers (JWT signing only)
   - `FERNET_SECRET` — 32+ chars, must differ from `JWT_SECRET`
   - `REDIS_PASSWORD`, `MONGODB_PASSWORD`, `POSTGRES_PASSWORD` (if Postgres enabled)
   - `RABBITMQ_PASSWORD` — 16+ chars (Celery / RabbitMQ always run in prod)
   - `REDIS_CACHE_URL` pointing at the `redis-cache` service (cache isolation)
4. `CORS_ORIGINS` — explicit HTTPS origins (no `*`).
5. `RUN_MIGRATIONS=false` and `RUN_SEED=false` — schema work goes through the one-shot `migrate` service, not API boot seed.

Process env overrides dotenv when you inject secrets without editing `.env`. Full variable list: [Configuration](/reference/configuration).

## 3. Start stack

**Why:** One Make target builds images, runs migrations, builds the SPA into a volume, then brings nginx + API + workers up detached.

```bash
make prod              # docker-compose.prod.yml + cache overlay, detached
make prod-cloudflare   # same + :443 origin TLS for Cloudflare Full (strict)
```

Equivalent of `make prod`:

```bash
DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 \
  docker compose -f docker-compose.prod.yml -f docker-compose.cache.yml up --build -d
```

**Always started** (no Compose profiles on these services):

| Service | Role |
|---------|------|
| `mongodb`, `redis`, `redis-cache`, `rabbitmq` | Data / cache / broker |
| `migrate` | One-shot DB init; exits 0 before app containers start |
| `server` | FastAPI (uvicorn, 4 workers) |
| `worker`, `beat` | Celery worker + beat |
| `todobot` | Telegram bot |
| `client` | One-shot SPA build into `client_dist` volume |
| `nginx` | Publishes `:80`, serves SPA, proxies `/api` |

Boot order (depends_on): Mongo healthy → `migrate` completes → `server` / `worker` / `beat` / `todobot` start; `client` completes → `nginx` starts once `server` is healthy.

Cloudflare edge (DNS, origin certs, Real-IP): [Cloudflare](/operations/cloudflare).

## 4. First-boot extras

**Why:** Migrations run automatically; admin user and search backfill do not.

```bash
# Bootstrap admin once (requires SEED_PASSWORD in .env)
make seed

# Backfill search index after first deploy or schema changes
make reindex-search
```

Resume chunks upsert on API startup when `AI_SEARCH_ENABLED=true`. Other sources index on create/update; `reindex-search` backfills existing rows.

## 5. Verify

**Why:** Confirm containers are up and the edge can reach the API.

```bash
docker compose -f docker-compose.prod.yml ps

curl -sf http://127.0.0.1/api/health
curl -sf http://127.0.0.1/api/ready
# or, with a public domain / Cloudflare:
curl -sf https://your-domain/api/health
curl -sf https://your-domain/api/ready
```

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health` | Liveness |
| `GET /api/ready` | MongoDB, Redis, broker readiness; Redis memory warnings |

Success: long-running services `running` / healthy; `migrate` and `client` exited 0; both curls return HTTP 200.

## 6. Day-2 ops

**Why:** Bare `make logs` / `make down` use default compose files and **omit** `docker-compose.prod.yml`. Prefer explicit `-f` for prod.

```bash
# Logs (follow)
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml logs -f server nginx

# Stop (keeps volumes)
docker compose -f docker-compose.prod.yml down

# Rebuild and restart after image/code changes
make prod
# or Cloudflare overlay:
make prod-cloudflare
```

Exec into a service (example for Celery / seed helpers that use `docker compose exec`):

```bash
docker compose -f docker-compose.prod.yml exec server sh
```

Backups and restore: [Backup & restore](/operations/backup-restore). Migrations detail: [Database](/operations/database).

## 7. Optional add-ons

| Add-on | How | Needs |
|--------|-----|-------|
| Postgres secondary | `docker compose -f docker-compose.prod.yml -f docker-compose.cache.yml --profile postgres up --build -d` | `ENABLE_POSTGRES=true`, `DATABASE_URL`, `POSTGRES_*` |
| AI search | Env flags below + `make reindex-search` | `GROQ_API_KEY` |
| Cloudflare origin TLS | `make prod-cloudflare` | Origin cert under `deploy/cloudflare/` — see [Cloudflare](/operations/cloudflare) |

**Not profiled in prod:** `worker`, `beat`, and `todobot` always start with `make prod`. Configure `TELEGRAM_BOT_TO_DO_TOKEN` (and allowed user ID) so the bot does not crash-loop; set Celery broker URL / RabbitMQ password as in the env template.

### AI search in production

Set in `.env`:

- `AI_SEARCH_ENABLED=true`
- `GROQ_API_KEY=...`
- `VITE_AI_SEARCH_ENABLED=true` (UI only; rebuild client via `make prod`)

Run `make reindex-search` after deploy or schema changes.

---

## Sentry releases (optional CI)

Client sourcemap upload is gated on GitHub Actions secrets (workflow [`sentry-release.yml`](../../.github/workflows/sentry-release.yml)):

| Secret / env | Purpose |
|--------------|---------|
| `SENTRY_AUTH_TOKEN` | Auth for `@sentry/vite-plugin` (required to run the job) |
| `SENTRY_ORG` / `SENTRY_PROJECT` | Sentry org and project slugs |
| `VITE_CLIENT_SENTRY_DSN` | Runtime DSN (build-time Vite env on the deploy host, not the upload token) |
| `SERVER_SENTRY_DSN` | Server/worker DSN on the API host |
| `SERVER_SENTRY_RELEASE` / `VITE_CLIENT_SENTRY_RELEASE` | Same release string on client build and server so events group |

The workflow is **disabled during development** (`if: false`, no `v*` tag trigger). Before production, restore the tag trigger and job `if` in [`sentry-release.yml`](../../.github/workflows/sentry-release.yml), then run **Actions → sentry-release → Run workflow** or push a `v*` tag. Without `SENTRY_AUTH_TOKEN`, the job stays skipped. Staging still needs a manual deliberate-500 check after deploy.

## Staging manual checks (P3)

Not automated in CI — run after deploy when credentials are available:

- Beat schedule firing on cron
- Telegram bot E2E (`app/todobot/`)
- Live Sentry — deliberate 500 in staging
- Stripe live mode (test mode in CI)
- Celery DLQ inspect/replay (below)

Full tier matrix: [Testing — P3](/reference/testing#p3-staging-manual-deferred-from-ci).

## Celery dead-letter queue

Workers consume only the durable `celery` queue (`-Q celery`). Final task failures publish a JSON payload to `celery.dlq` (also used as the RabbitMQ DLX target for rejected messages). Workers never consume the DLQ.

**Upgrade note:** Changing queue arguments requires recreating the queue once if an old `celery` queue already exists without DLX args:

```bash
docker compose -f docker-compose.prod.yml exec rabbitmq rabbitmqctl delete_queue celery
# restart worker so Celery redeclares the queue with DLX args
```

**Inspect:**

```bash
docker compose -f docker-compose.prod.yml exec rabbitmq rabbitmqctl list_queues name messages consumers
```

Management UI (when exposed): queue `celery.dlq` → get messages; copy `task` / `args` / `kwargs` from the JSON body.

**Replay a DLQ payload** (manual):

```bash
docker compose -f docker-compose.prod.yml exec server python -c "
from app.workers.celery_app import celery_app
celery_app.send_task('TASK_NAME', args=[...], kwargs={...})
"
```

Replace `TASK_NAME` / args from the DLQ message. After a successful replay, ack/purge that DLQ message in the management UI.

## Related

- [Database](/operations/database) — migrations and seeds
- [Backup & restore](/operations/backup-restore)
- [Cloudflare](/operations/cloudflare)
- [Security](/reference/security)
- [DevOps checklist](/operations/devops-checklist)
