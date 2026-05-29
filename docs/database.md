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

Do **not** put application seed data in migrations unless required for constraints. Use [`server/app/db/seed.py`](../server/app/db/seed.py) instead.

## Extensions on existing databases

Init SQL runs only when the Postgres data directory is created. Databases that already exist get extensions from the Alembic revision `c9d0e1f2a3b4` (`CREATE EXTENSION IF NOT EXISTS pg_trgm`).

To recreate everything from scratch:

```bash
make db-reset
make seed
```

## Tests

pytest uses SQLite (`create_all` / `drop_all`) in [`server/tests/conftest.py`](../server/tests/conftest.py), not Postgres. Postgres-only features (e.g. GIN full-text indexes) are not exercised in the default test run.
