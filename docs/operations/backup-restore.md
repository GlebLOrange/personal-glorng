# Backup & restore

Automated backups and manual prod → dev restore.

## Daily backup script

[`scripts/db_maintenance.sh`](../../scripts/db_maintenance.sh) backs up **MongoDB** (primary), Redis, and media, rotates old files, verifies dumps, optionally copies offsite, then runs migrations. When `ENABLE_POSTGRES=true`, it also backs up Postgres (secondary). Dumps run **before** migrate so a failed migrate still leaves a pre-change archive.

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

**Not source of truth:** Elasticsearch (rebuild with `make reindex-search`), Redis sessions/rate-limits (optional), `.env` (password manager — never next to dumps).

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
| `BACKUP_OFFSITE_CMD` | _(empty)_ | Shell command after verify (e.g. rsync); failure fails the run |
| `BACKUP_REQUIRE_OFFSITE` | `false` | When `true`, fail if `BACKUP_OFFSITE_CMD` is empty (use on prod) |

The script brings up `mongodb` and `redis` before dumping. With Postgres enabled it uses `--profile postgres` for the `db` service. Empty dumps fail; `.gz` archives are checked with `gzip -t`. Cron install injects `PATH`/`HOME` so `docker compose` resolves under cron (`BACKUP_CRON_PATH` / `BACKUP_CRON_HOME` override).

### Operator loop (durable)

1. On the prod host, set `BACKUP_COMPOSE_FILE` to the compose file that is actually running.
2. Run `make backup` once; confirm `backups/mongodb/proj_portfolio_mongo_latest.archive.gz` is non-empty.
3. Set `BACKUP_OFFSITE_CMD` (no `--delete`) and `BACKUP_REQUIRE_OFFSITE=true` for prod.
4. `make backup-install` (04:20 Europe/Warsaw). Confirm `crontab -l` and that cron’s `PATH` can see `docker`.
5. Confirm Telegram “DB maintenance OK/FAILED”.
6. Run a restore drill on a **throwaway** volume (below). Record the date.

RPO for this site: last good daily Mongo + media. Redis is optional.

### Offsite copy

Local disk alone is not durable. Set `BACKUP_OFFSITE_CMD` to any command that copies `$BACKUP_DIR` (or the latest dumps) elsewhere. **Do not use `rsync --delete`** — a wiped or corrupt local tree must not erase the last good remote.

```bash
# .env — rsync to another host (no --delete)
BACKUP_OFFSITE_CMD='rsync -az ./backups/ user@offsite:/var/backups/glorng/'
BACKUP_REQUIRE_OFFSITE=true

# Or rclone / restic as a command string only (no new repo dependency)
# BACKUP_OFFSITE_CMD='rclone copy ./backups/ remote:glorng-backups'

# Dry-run / CI smoke: succeed without copying
BACKUP_OFFSITE_CMD='true'
```

If `BACKUP_OFFSITE_CMD` is empty, the script logs a warning (first local run still works). With `BACKUP_REQUIRE_OFFSITE=true`, an empty command fails the run and Telegram reports failure. No S3/restic dependency is baked in — use whatever the host already has.

## Restore MongoDB (primary)

Run during a maintenance window. `--drop` replaces collections in the archive with backup contents. **Never use this as the first restore drill** — drill on a throwaway volume first.

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

Then restart app services and confirm `/api/health`.

### Restore drill (throwaway — copy-paste)

Use a separate Compose project so volumes do not collide with prod:

```bash
# 1) Fresh dump (or copy *_latest.archive.gz onto the drill host)
make backup

# 2) Throwaway Mongo (project name prefixes volumes: glorng-drill_*)
docker compose -f docker-compose.prod.yml -p glorng-drill up -d mongodb
# Wait until healthy, then restore into the drill instance:
gunzip -c backups/mongodb/proj_portfolio_mongo_latest.archive.gz \
  | docker compose -f docker-compose.prod.yml -p glorng-drill exec -T mongodb mongorestore \
      --username "$MONGODB_USER" \
      --password "$MONGODB_PASSWORD" \
      --authenticationDatabase admin \
      --archive \
      --drop

# 3) Optional media into a spare volume (not live MEDIA_DIR)
mkdir -p /tmp/glorng-media-drill
tar xzf backups/media/proj_portfolio_media_latest.tar.gz -C /tmp/glorng-media-drill

# 4) Point a throwaway API at the drill Mongo (or mongosh spot-check login/tasks/recipes)
# 5) Tear down when done:
docker compose -f docker-compose.prod.yml -p glorng-drill down -v
```

Skip Redis restore unless you need blacklist/rate-limit replay from that point in time.

### Restore drill checklist

1. Take a fresh `make backup` (or copy `*_latest.archive.gz`).
2. Restore into a non-production Mongo (`-p glorng-drill` or empty volume).
3. Confirm login + one domain read (e.g. recipes or tasks), or `mongosh` spot-check.
4. Record date and outcome below (and in the deploy notes / PR that changes backup tooling).

**Last restore drill:** _yyyy-mm-dd — operator fills after drill_

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

- **MongoDB:** use `mongorestore --archive --drop` as above; full-instance archives restore all databases in the dump. Drill on a separate `-p` project first.
- **Postgres:** use `pg_restore` against a stopped or empty target DB (script handles the local secondary flow).
- **Redis:** skip unless needed; replace `dump.rdb` only during maintenance — token blacklist and rate-limit state will match backup time.
- **Media:** extract tarball into a spare directory or volume first; only then into live `MEDIA_DIR`.

## Related

- [Database](/operations/database)
- [Deployment](/operations/deployment)
- [DevOps checklist](/operations/devops-checklist)
