# Database

PostgreSQL holds application state. Schema changes are managed with **Alembic**; reference data uses optional **seed** scripts.

## Connection

| Context | URL |
|---------|-----|
| Docker services | `DATABASE_URL` in `.env` (host `db`, port `5432`) |
| Host tools (psql, GUI) | `localhost:5433` (dev compose maps `5433:5432`) |

Credentials come from `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` in `.env`.

## Bootstrap flow

```mermaid
flowchart TD
  DB[(Postgres volume)]
  InitSQL[initdb.d extensions]
  Migrate[migrate service]
  Server[server optional RUN_MIGRATIONS]
  InitSQL -->|first volume only| DB
  Migrate -->|alembic upgrade head| DB
  Server -->|dev convenience| DB
```

1. **Postgres** starts with an empty database (or existing `pgdata` volume).
2. **First volume only:** [`server/app/db/init/01_extensions.sql`](../server/app/db/init/01_extensions.sql) installs extensions (e.g. `pg_trgm`).
3. **`migrate` service** runs [`server/scripts/db_init.sh`](../server/scripts/db_init.sh): wait for Postgres, then `alembic upgrade head`.
4. **App services** (`server`, `worker`, `todobot`) start after `migrate` completes successfully.

### Dev vs production

| Environment | Migrations |
|-------------|------------|
| **Dev** (`docker-compose.yml`) | `migrate` service runs on stack start; `server` also has `RUN_MIGRATIONS=true` so `make dev-lite` (db + redis + server only) still migrates if `migrate` was skipped. |
| **Prod** (`docker-compose.prod.yml`) | Only the `migrate` service runs migrations; `RUN_MIGRATIONS=false` on app containers. |

## Make targets

| Command | Description |
|---------|-------------|
| `make db-init` | Run migrations only (`docker compose run --rm migrate`) |
| `make migrate` | Alias for `db-init` |
| `make db-reset` | Drop volumes, start db, migrate (destructive) |
| `make db-revision msg='add foo'` | Autogenerate Alembic revision |
| `make db-current` | Show current revision |
| `make db-downgrade` | Roll back one revision (dev) |
| `make db-check` | Verify migration graph (`alembic check`) |
| `make seed` | Idempotent admin user + sample recipes (requires running server) |
| `make seed-multicooker-recipes` | Import multicooker recipes from TheMealDB |

To migrate and seed in one shot (first-time dev):

```bash
RUN_SEED=true make db-init
```

## Model change workflow

1. Edit SQLAlchemy models under [`server/app/db/models/`](../server/app/db/models/).
2. `make db-revision msg='describe change'`
3. Review the generated file in [`server/app/db/migrations/versions/`](../server/app/db/migrations/versions/).
4. `make db-init`
5. Run tests: `make test`

Do **not** put application seed data in migrations unless required for constraints. Use [`server/app/db/seed/run.py`](../server/app/db/seed/run.py) instead.

## Extensions on existing databases

Init SQL runs only when the Postgres data directory is created. Databases that already exist get extensions from the Alembic revision `c9d0e1f2a3b4` (`CREATE EXTENSION IF NOT EXISTS pg_trgm`).

To recreate everything from scratch:

```bash
make db-reset
make seed
```

## Tests

pytest uses SQLite (`create_all` / `drop_all`) in [`server/tests/conftest.py`](../server/tests/conftest.py), not Postgres. Postgres-only features (e.g. GIN full-text indexes) are not exercised in the default test run.

Optional Postgres integration tests:

```bash
export POSTGRES_TEST_URL=postgresql+asyncpg://user:pass@localhost:5433/glorng
cd server && uv run pytest -m postgres -v
```

Without `POSTGRES_TEST_URL`, `@pytest.mark.postgres` tests are skipped.

## Backups and daily maintenance

Production stack: migrate schema, then dump Postgres, Redis, and media. Scheduled daily at **04:20** (`Europe/Warsaw` by default).

| Command | Description |
|---------|-------------|
| `make backup` | Run [`scripts/db_maintenance.sh`](../scripts/db_maintenance.sh) once |
| `make backup-install` | Install host cron via [`scripts/install_backup_cron.sh`](../scripts/install_backup_cron.sh) |
| `make db-pull-prod` | Restore prod dump into local dev (requires `CONFIRM_PROD_PULL=1`) |

Configure in `.env`: `BACKUP_DIR`, `BACKUP_RETENTION_DAYS`, `BACKUP_RETENTION_WEEKS`, `BACKUP_COMPOSE_FILE`, `BACKUP_NOTIFY`, `BACKUP_TIMEZONE`.

**What the maintenance script does:**

1. Acquire lock (skip if already running)
2. `alembic upgrade head` via the `migrate` service
3. `pg_dump` custom format → `backups/postgres/glorng_YYYY-MM-DD_HHMM.dump.gz`
4. Redis `SAVE` → `backups/redis/`
5. `server_media` volume tarball → `backups/media/`
6. Rotate old files (keep daily + Sunday weekly copies)
7. `pg_restore --list` integrity check
8. Optional Telegram alert via [`notify_admin`](../server/app/core/telegram.py)

**Restore Postgres from latest backup:**

```bash
gunzip -c backups/postgres/glorng_latest.dump.gz | \
  docker compose -f docker-compose.prod.yml exec -T db pg_restore \
  -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner
```

**Pull prod into local dev** (manual, destructive to local data):

```bash
CONFIRM_PROD_PULL=1 PROD_SSH_HOST=user@prod make db-pull-prod
# or: CONFIRM_PROD_PULL=1 PROD_BACKUP_PATH=/path/to/glorng_latest.dump.gz make db-pull-prod
```
