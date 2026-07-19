# Backup & restore

Automated backups and manual prod → dev restore.

## Daily backup script

[`scripts/db_maintenance.sh`](../../scripts/db_maintenance.sh) runs migrations, backs up **MongoDB** (primary), Redis, and media, rotates old files, verifies dumps, and optionally notifies. When `ENABLE_POSTGRES=true`, it also backs up Postgres (secondary).

```bash
make backup           # run once
make backup-install   # install cron via scripts/install_backup_cron.sh
```

### What gets backed up

| Asset | When | Output path pattern |
|-------|------|---------------------|
| MongoDB archive | Always | `backups/mongodb/proj_portfolio_mongo_YYYY-MM-DD_HHMM.archive.gz` |
| Postgres | `ENABLE_POSTGRES=true` | `backups/postgres/proj_portfolio_YYYY-MM-DD_HHMM.dump.gz` |
| Redis RDB | Always | `backups/redis/proj_portfolio_redis_*.rdb` |
| Media volume | Always | `backups/media/proj_portfolio_media_*.tar.gz` |

Symlinks `*_latest.*` point to the newest dump per type. Mongo and Postgres keep Sunday copies for `BACKUP_RETENTION_WEEKS`.

### Configuration (`.env`)

| Variable | Default | Purpose |
|----------|---------|---------|
| `MONGODB_USER` / `MONGODB_PASSWORD` | — | Required for Mongo dump/verify |
| `REDIS_PASSWORD` | — | Required for Redis dump |
| `ENABLE_POSTGRES` | `false` | When `true`, also dump/verify Postgres |
| `POSTGRES_*` | — | Required only when Postgres backups are enabled |
| `BACKUP_DIR` | `./backups` | Root backup directory |
| `BACKUP_COMPOSE_FILE` | `docker-compose.prod.yml` | Compose file for `mongodb` / `redis` / optional `db` |
| `BACKUP_RETENTION_DAYS` | `7` | Daily retention |
| `BACKUP_RETENTION_WEEKS` | `4` | Weekly Sunday copies kept longer |
| `BACKUP_NOTIFY` | `true` | Telegram notify on result |
| `BACKUP_TIMEZONE` | `Europe/Warsaw` | Cron timezone |

The script brings up `mongodb` and `redis` before dumping. With Postgres enabled it uses `--profile postgres` for the `db` service.

## Restore MongoDB (primary)

Run during a maintenance window. `--drop` replaces collections in the archive with backup contents.

```bash
# From repo root, with prod compose + .env loaded:
gunzip -c backups/mongodb/proj_portfolio_mongo_latest.archive.gz \
  | docker compose -f docker-compose.prod.yml exec -T mongodb mongorestore \
      --username "$MONGODB_USER" \
      --password "$MONGODB_PASSWORD" \
      --authenticationDatabase admin \
      --archive \
      --drop
```

Then restart app services and confirm `/api/health`. Prefer restoring onto a throwaway volume first when drilling recovery.

### Restore drill checklist

1. Take a fresh `make backup` (or copy `*_latest.archive.gz`).
2. Restore into a non-production Mongo (empty volume or separate compose project).
3. Point a throwaway API at that DB and confirm login + one domain read (e.g. recipes or tasks).
4. Record date and outcome in the deploy notes / PR that changes backup tooling.

## Pull prod backup to local dev

[`scripts/pull_prod_db.sh`](../../scripts/pull_prod_db.sh) — **manual only**, never schedule on production. This path restores **Postgres** dumps into local secondary Postgres.

```bash
# .env
CONFIRM_PROD_PULL=1
PROD_BACKUP_PATH=/path/to/glorng_latest.dump.gz
# or fetch via SSH:
# PROD_SSH_HOST=user@prod-host
# PROD_BACKUP_DIR=/var/backups/glorng/postgres/glorng_latest.dump.gz

make db-pull-prod
```

For Mongo prod → local, copy the `.archive.gz` and use `mongorestore` against local `mongodb` (same flags as above, with the lite/dev compose file).

## Restore notes

- **MongoDB:** use `mongorestore --archive --drop` as above; full-instance archives restore all databases in the dump.
- **Postgres:** use `pg_restore` against a stopped or empty target DB (script handles the local secondary flow).
- **Redis:** replace `dump.rdb` only during maintenance; token blacklist and rate-limit state will match backup time.
- **Media:** extract tarball into the media volume path configured by `MEDIA_DIR`.

## Related

- [Database](/operations/database)
- [Deployment](/operations/deployment)
