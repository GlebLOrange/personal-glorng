# Backup & restore

Automated backups and manual prod → dev restore.

## Daily backup script

[`scripts/db_maintenance.sh`](../../scripts/db_maintenance.sh) runs migrations, backs up Postgres/Redis/media, rotates old files, verifies Postgres dumps, and optionally notifies.

```bash
make backup           # run once
make backup-install   # install cron via scripts/install_backup_cron.sh
```

### What gets backed up

| Asset | Output path pattern |
|-------|---------------------|
| Postgres | `backups/postgres/proj_portfolio_YYYY-MM-DD_HHMMSS.dump.gz` |
| Redis RDB | `backups/redis/proj_portfolio_redis_*.rdb` |
| Media volume | `backups/media/proj_portfolio_media_*.tar.gz` |

Symlinks `*_latest.*` point to the newest dump per type.

### Configuration (`.env`)

| Variable | Default | Purpose |
|----------|---------|---------|
| `BACKUP_DIR` | `./backups` | Root backup directory |
| `BACKUP_COMPOSE_FILE` | `docker-compose.prod.yml` | Compose file for `db`/`redis` services |
| `BACKUP_RETENTION_DAYS` | `7` | Daily retention |
| `BACKUP_RETENTION_WEEKS` | `4` | Weekly Sunday copies kept longer |
| `BACKUP_NOTIFY` | `true` | Telegram notify on result |
| `BACKUP_TIMEZONE` | `Europe/Warsaw` | Cron timezone |

Requires `POSTGRES_*` and `REDIS_PASSWORD` in `.env`. The script brings up `db` and `redis` before dumping.

## Pull prod backup to local dev

[`scripts/pull_prod_db.sh`](../../scripts/pull_prod_db.sh) — **manual only**, never schedule on production.

```bash
# .env
CONFIRM_PROD_PULL=1
PROD_BACKUP_PATH=/path/to/glorng_latest.dump.gz
# or fetch via SSH:
# PROD_SSH_HOST=user@prod-host
# PROD_BACKUP_DIR=/var/backups/glorng/postgres/glorng_latest.dump.gz

make db-pull-prod
```

Restores into local dev Postgres. Use only with trusted backup files.

## Restore notes

- Postgres: use `pg_restore` against a stopped or empty target DB (script handles the local dev flow).
- Redis: replace `dump.rdb` only during maintenance; token blacklist and rate-limit state will match backup time.
- Media: extract tarball into the media volume path configured by `MEDIA_DIR`.

## Related

- [Database](/operations/database)
- [Deployment](/operations/deployment)
