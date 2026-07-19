# Deployment

Production runbook for the Docker Compose stack.

## Prerequisites

1. Copy [`.env.production.example`](../../.env.production.example) (or `.env.example`) to `.env` and fill blanks (`APP_ENV=production`).
2. Set strong secrets — production startup validates:
   - `JWT_SECRET` — 32+ chars, no weak markers (JWT signing only)
   - `FERNET_SECRET` — 32+ chars, must differ from `JWT_SECRET`
   - `REDIS_PASSWORD`, `MONGODB_PASSWORD`, `POSTGRES_PASSWORD` (if Postgres enabled)
   - `RABBITMQ_PASSWORD` — 16+ chars when Celery is used
   - Set `REDIS_CACHE_URL` to the `redis-cache` service for cache isolation
3. Set `CORS_ORIGINS` to explicit HTTPS origins (no `*`).
4. Set `RUN_MIGRATIONS=false` and `RUN_SEED=false` (migrations run via `migrate` service only).
5. Prod compose enables log rotation (`10m` × 3), `no-new-privileges`, and `init` on services. Process env overrides dotenv when you inject secrets without editing `.env`.

See [Configuration](/reference/configuration) for the full variable list.

## Start production

```bash
make prod              # docker-compose.prod.yml
make prod-cloudflare   # + origin TLS on :443 for Cloudflare Full (strict)
```

Cloudflare edge setup: [Cloudflare](/operations/cloudflare).

Compose service names for the base stack are listed in the [architecture inventory (generated)](/generated/architecture-inventory).

## Sentry releases (optional CI)

Client sourcemap upload is gated on GitHub Actions secrets (workflow [`sentry-release.yml`](../../.github/workflows/sentry-release.yml)):

| Secret / env | Purpose |
|--------------|---------|
| `SENTRY_AUTH_TOKEN` | Auth for `@sentry/vite-plugin` (required to run the job) |
| `SENTRY_ORG` / `SENTRY_PROJECT` | Sentry org and project slugs |
| `VITE_CLIENT_SENTRY_DSN` | Runtime DSN (build-time Vite env on the deploy host, not the upload token) |
| `SERVER_SENTRY_DSN` | Server/worker DSN on the API host |
| `SERVER_SENTRY_RELEASE` / `VITE_CLIENT_SENTRY_RELEASE` | Same release string on client build and server so events group |

Trigger: **Actions → sentry-release → Run workflow**, or push a `v*` tag. Without `SENTRY_AUTH_TOKEN`, the job is skipped (CI stays green). Staging still needs a manual deliberate-500 check after deploy.

## First-deploy checklist

```bash
# 1. Start stack (migrate service runs on boot)
make prod

# 2. Seed bootstrap admin once (if not already seeded)
make seed

# 3. Backfill search index
make reindex-search

# 4. Smoke checks
curl -sf https://your-domain/api/health
curl -sf https://your-domain/api/ready
```

Resume chunks upsert on API startup when `AI_SEARCH_ENABLED=true`. Other sources index on create/update; `reindex-search` backfills existing rows.

## Health endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health` | Liveness |
| `GET /api/ready` | MongoDB, Redis, broker readiness; Redis memory warnings |

## Optional compose profiles

| Profile | Command | Needs |
|---------|---------|-------|
| Worker + beat | `docker compose -f docker-compose.prod.yml --profile worker up -d` | RabbitMQ, `CELERY_BROKER_URL` |
| Telegram bot | `--profile bot` | `TELEGRAM_BOT_TO_DO_TOKEN`, allowed user ID |
| Postgres secondary | `--profile postgres` | `ENABLE_POSTGRES=true`, `DATABASE_URL` |
| Search (Elasticsearch) | search compose overlay + `ELASTICSEARCH_URL` | `make dev-search` pattern for prod overlay |

## AI search in production

Set in `.env`:

- `AI_SEARCH_ENABLED=true`
- `GROQ_API_KEY=...`
- `VITE_AI_SEARCH_ENABLED=true` (UI only)

Run `make reindex-search` after deploy or schema changes.

## Staging manual checks (P3)

Not automated in CI — run after deploy when credentials are available:

- Beat schedule firing on cron
- Telegram bot E2E (`app/todobot/`)
- Live Sentry — deliberate 500 in staging
- Stripe live mode (test mode in CI)
- Celery DLQ inspect/replay (below)

## Celery dead-letter queue

Workers consume only the durable `celery` queue (`-Q celery`). Final task failures publish a JSON payload to `celery.dlq` (also used as the RabbitMQ DLX target for rejected messages). Workers never consume the DLQ.

**Upgrade note:** Changing queue arguments requires recreating the queue once if an old `celery` queue already exists without DLX args:

```bash
docker compose exec rabbitmq rabbitmqctl delete_queue celery
# restart worker so Celery redeclares the queue with DLX args
```

**Inspect:**

```bash
docker compose exec rabbitmq rabbitmqctl list_queues name messages consumers
```

Management UI (when exposed): queue `celery.dlq` → get messages; copy `task` / `args` / `kwargs` from the JSON body.

**Replay a DLQ payload** (manual):

```bash
docker compose exec server python -c "
from app.workers.celery_app import celery_app
celery_app.send_task('TASK_NAME', args=[...], kwargs={...})
"
```

Replace `TASK_NAME` / args from the DLQ message. After a successful replay, ack/purge that DLQ message in the management UI.


Full tier matrix: [Testing — P3](/reference/testing#p3-staging-manual-deferred-from-ci).

## Related

- [Database](/operations/database) — migrations and seeds
- [Backup & restore](/operations/backup-restore)
- [Security](/reference/security)
- [DevOps checklist](/operations/devops-checklist)
