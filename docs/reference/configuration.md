# Configuration

Environment variable reference. Canonical template: [`.env.example`](../../.env.example). Validation logic: [`server/app/settings.py`](../../server/app/settings.py).

Copy for local dev:

```bash
cp .env.example .env
```

`RUN_MIGRATIONS` and `RUN_SEED` are read from `.env` only — not Docker Compose overrides.

## App

| Variable | Default (example) | Purpose |
|----------|-------------------|---------|
| `APP_ENV` | `development` | `development`, `staging`, `production`, `test` |
| `APP_NAME` | `Gleb.Y` | Display name |
| `BASE_URL` | `http://localhost` | Absolute URL for links and redirects |
| `MEDIA_DIR` | `/app/media` | Uploaded file storage path |
| `CORS_ORIGINS` | localhost variants | Comma-separated allowed origins (required explicit list in production) |
| `LOG_REQUESTS` | `true` | Log request start/complete |
| `LOG_REQUEST_BODIES` | `false` | Log redacted JSON bodies (POST/PUT/PATCH) |
| `APP_LOG_PERSIST_ENABLED` | `true` | Persist structured logs to MongoDB |
| `APP_LOG_PERSIST_MIN_LEVEL` | `INFO` | Min level for DB log persistence |
| `APP_LOG_RETENTION_DAYS` | `30` | TTL for `app_logs` collection |

## Database bootstrap

| Variable | Default | Purpose |
|----------|---------|---------|
| `ENABLE_MONGODB` | `true` | Primary datastore |
| `ENABLE_POSTGRES` | `false` | Secondary FTS + audit |
| `PRIMARY_DATABASE` | `mongodb` | Primary backend name |
| `RUN_MIGRATIONS` | `true` (dev) | Server-side migration on boot (dev only; prod uses `migrate` service) |
| `RUN_SEED` | `true` (dev) | Seed on server boot (dev only) |
| `SEED_DEMO_COUNT` | `50` | Demo seed volume |

## MongoDB

| Variable | Purpose |
|----------|---------|
| `MONGODB_USER`, `MONGODB_PASSWORD`, `MONGODB_DB` | Credentials and database name |
| `MONGODB_URL` | Connection string (Docker host `mongodb`) |

## PostgreSQL (optional)

| Variable | Purpose |
|----------|---------|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Credentials |
| `DATABASE_URL` | `postgresql+asyncpg://...` (host `db` in Docker, `localhost:5433` on host) |

Enable with `ENABLE_POSTGRES=true` and `make dev-postgres` or `--profile postgres`.

## Elasticsearch (optional)

| Variable | Default | Purpose |
|----------|---------|---------|
| `ELASTICSEARCH_URL` | empty | Leave empty for dev-lite; set for `make dev-search` |
| `ELASTICSEARCH_INDEX` | `search_documents` | Index name |

## Redis

| Variable | Purpose |
|----------|---------|
| `REDIS_PASSWORD` | Auth (validated in production) |
| `REDIS_URL` | `redis://:password@redis:6379/0` |

## RabbitMQ / Celery

| Variable | Purpose |
|----------|---------|
| `RABBITMQ_USER`, `RABBITMQ_PASSWORD` | Broker credentials (`RABBITMQ_PASSWORD` min 16 chars in production) |
| `CELERY_BROKER_URL` | AMQP URL |
| `CELERY_TASK_ALWAYS_EAGER` | `true` in ultra-lite host API (inline tasks, no broker) |

## Auth & JWT

| Variable | Default | Purpose |
|----------|---------|---------|
| `JWT_SECRET` | — | **Required.** 32+ chars in production |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `JWT_ALGORITHM` | `HS256` | Signing algorithm |
| `FIREBASE_AUTH_ENABLED` | `false` | Google sign-in via Firebase |
| `FIREBASE_PROJECT_ID` | | Firebase project |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | | Service account JSON (prefer `GOOGLE_APPLICATION_CREDENTIALS` in deploy) |

## Email

| Variable | Default | Purpose |
|----------|---------|---------|
| `EMAIL_BACKEND` | `console` | `console` or `smtp` |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | | SMTP settings when backend is `smtp` |

## Sentry

| Variable | Default | Purpose |
|----------|---------|---------|
| `SENTRY_ENABLED` | `false` | Enable server Sentry |
| `SERVER_SENTRY_DSN` | | DSN |
| `SERVER_SENTRY_RELEASE` | | Release tag |

Client: `VITE_SENTRY_*` in `client/.env.development` or commented block in `.env.example`.

## Telegram bot

| Variable | Purpose |
|----------|---------|
| `TELEGRAM_BOT_TO_DO_TOKEN` | Todobot token (`make dev-bot`) |
| `TELEGRAM_BOT_CHAT_TOKEN` | Optional chat notifications |
| `TELEGRAM_ALLOWED_USER_ID` | Whitelist Telegram user ID |
| `TIMEZONE` | `Europe/Warsaw` — scheduling |
| `EXPENSE_DEFAULT_CURRENCY` | `PLN` |
| `TASK_INTAKE_AI_ENABLED` | AI-assisted task parsing in bot |
| `TASK_INTAKE_CONFIDENCE_THRESHOLD` | `0.7` |

## OAuth integrations

| Variable | Purpose |
|----------|---------|
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` | Google Calendar |
| `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_REDIRECT_URI` | GitHub OAuth |
| `GITHUB_ALLOWED_USERS` | Comma-separated GitHub usernames allowed to link |
| `GITHUB_PUBLIC_USERNAME` | Public repos widget |

## AI (Groq)

| Variable | Default | Purpose |
|----------|---------|---------|
| `GROQ_API_KEY` | | Required when AI features enabled |
| `GROQ_CHAT_MODEL` | `llama-3.3-70b-versatile` | Model id |
| `GROQ_API_BASE_URL` | `https://api.groq.com/openai/v1` | API base URL |
| `AI_CHAT_ENABLED` | `true` | Admin AI chat |
| `AI_SEARCH_ENABLED` | `true` | Public search chat |

Client mirrors: `VITE_AI_CHAT_ENABLED`, `VITE_AI_SEARCH_ENABLED`.

## News ingest

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEWS_INGEST_ENABLED` | `false` | Curated news worker |
| `NEWS_SOURCES_JSON` | `[]` | Source definitions |
| `NEWS_INGEST_MAX_ITEMS_PER_RUN` | `10` | Batch size |
| `NEWS_TELEGRAM_BOT_TOKEN`, `NEWS_TELEGRAM_CHANNEL_ID` | | Publish channel |

## Donations

| Variable | Purpose |
|----------|---------|
| `STRIPE_LINK` | Legacy donation link |
| `STRIPE_SECRET_KEY` | Checkout sessions |
| `STRIPE_WEBHOOK_SECRET` | Webhook signature |
| `STRIPE_DONATION_AMOUNT_CENTS`, `STRIPE_DONATION_CURRENCY` | Default amount |
| `STRIPE_CHECKOUT_SUCCESS_URL`, `STRIPE_CHECKOUT_CANCEL_URL` | Redirect URLs |
| `PAYPAL_DONATION_LINK`, `PATREON_LINK` | External links |
| `TELEGRAM_LINK`, `CRYPTO_BTC_ADDRESS`, `CRYPTO_ETH_ADDRESS` | Resume contact meta |

## Webhooks

| Variable | Purpose |
|----------|---------|
| `WEBHOOK_SECRETS` | JSON object `{"slug":"secret",...}` for `POST /api/webhooks/{slug}` |

## Spotify

| Variable | Purpose |
|----------|---------|
| `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REFRESH_TOKEN` | Now-playing banner |

## Weather

| Variable | Default | Purpose |
|----------|---------|---------|
| `WEATHER_DEFAULT_LABEL` | `Wrocław` | Default city label |
| `WEATHER_DEFAULT_QUERY` | `Wroclaw` | API query |
| `WORLD_TIME_API_BASE` | `https://timeapi.world/api` | Time API base |

## Seed / E2E

| Variable | Purpose |
|----------|---------|
| `ALLOWED_EMAIL` | Bootstrap admin email for `make seed` |
| `SEED_PASSWORD` | Admin password for seed |
| `E2E_EMAIL`, `E2E_PASSWORD` | Playwright credentials |

## Test-only

| Variable | Purpose |
|----------|---------|
| `USE_SQLITE_TESTS` | `false` — leave false in production |
| `POSTGRES_TEST_URL` | Integration tests with `@pytest.mark.postgres` |

## Frontend dev (host Vite)

Defaults in `client/.env.development`. Override via commented `VITE_*` block in `.env.example`:

- `VITE_API_PROXY_TARGET` — API proxy target (`http://127.0.0.1:8000`)
- `VITE_BEHIND_NGINX` — set when using nginx dev-lite
- `VITE_FIREBASE_*`, `VITE_SENTRY_*`, `VITE_AI_*` — client feature toggles

## Backups

Used by [`scripts/db_maintenance.sh`](../../scripts/db_maintenance.sh). Always dumps MongoDB (primary), Redis, and media; Postgres only when `ENABLE_POSTGRES=true`.

| Variable | Default | Purpose |
|----------|---------|---------|
| `MONGODB_USER` / `MONGODB_PASSWORD` | — | Required for Mongo dump/verify |
| `REDIS_PASSWORD` | — | Required for Redis dump |
| `BACKUP_DIR` | `./backups` | Backup root |
| `BACKUP_RETENTION_DAYS` | `7` | Daily retention |
| `BACKUP_RETENTION_WEEKS` | `4` | Weekly Sunday keepers (Mongo/Postgres) |
| `BACKUP_COMPOSE_FILE` | `docker-compose.prod.yml` | Compose file for backup |
| `BACKUP_NOTIFY` | `true` | Notify on result |
| `BACKUP_TIMEZONE` | `Europe/Warsaw` | Cron timezone |

See [Backup & restore](/operations/backup-restore).

## Prod → dev pull

Manual only — [`scripts/pull_prod_db.sh`](../../scripts/pull_prod_db.sh):

| Variable | Purpose |
|----------|---------|
| `CONFIRM_PROD_PULL` | Must be `1` to run |
| `PROD_BACKUP_PATH` | Local dump path |
| `PROD_SSH_HOST`, `PROD_BACKUP_DIR` | Fetch from remote |
| `LOCAL_COMPOSE_FILE` | Target compose file |

## Related

- [Security](/reference/security) — secret strength and production validation
- [Deployment](/operations/deployment)
- [Getting started](/guide/getting-started)
