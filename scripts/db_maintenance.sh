#!/usr/bin/env bash
# Daily DB maintenance: migrate, backup MongoDB/Redis/media (+ Postgres if enabled),
# rotate, verify, notify.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

log() {
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*" >&2
}

fail() {
  log "ERROR: $*"
  exit 1
}

postgres_enabled() {
  [[ "${ENABLE_POSTGRES:-false}" == "true" ]]
}

load_env() {
  if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
  fi

  : "${MONGODB_USER:?MONGODB_USER is required}"
  : "${MONGODB_PASSWORD:?MONGODB_PASSWORD is required}"
  : "${REDIS_PASSWORD:?REDIS_PASSWORD is required}"

  if postgres_enabled; then
    : "${POSTGRES_USER:?POSTGRES_USER is required when ENABLE_POSTGRES=true}"
    : "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required when ENABLE_POSTGRES=true}"
    : "${POSTGRES_DB:?POSTGRES_DB is required when ENABLE_POSTGRES=true}"
  fi

  BACKUP_DIR="${BACKUP_DIR:-./backups}"
  BACKUP_COMPOSE_FILE="${BACKUP_COMPOSE_FILE:-docker-compose.prod.yml}"
  BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
  BACKUP_RETENTION_WEEKS="${BACKUP_RETENTION_WEEKS:-4}"
  BACKUP_NOTIFY="${BACKUP_NOTIFY:-true}"
  BACKUP_OFFSITE_CMD="${BACKUP_OFFSITE_CMD:-}"
  LOCK_DIR="${BACKUP_DIR}/.db_maintenance.lock.d"
}

compose() {
  docker compose -f "$BACKUP_COMPOSE_FILE" "$@"
}

compose_postgres() {
  compose --profile postgres "$@"
}

ensure_stack_ready() {
  compose up -d mongodb redis
  compose exec -T mongodb mongosh \
    --username "$MONGODB_USER" \
    --password "$MONGODB_PASSWORD" \
    --authenticationDatabase admin \
    --quiet \
    --eval "db.adminCommand('ping').ok" >/dev/null

  if postgres_enabled; then
    compose_postgres up -d db
    compose_postgres exec -T db pg_isready -U "$POSTGRES_USER" >/dev/null
  fi
}

run_migrate() {
  log "Running migrate service (Mongo indexes; Alembic if Postgres enabled)"
  compose run --rm migrate
}

backup_mongodb() {
  local stamp="$1"
  local out_dir="$BACKUP_DIR/mongodb"
  local dump_path="$out_dir/proj_portfolio_mongo_${stamp}.archive.gz"
  mkdir -p "$out_dir"

  log "Backing up MongoDB to $dump_path"
  # Full instance archive (all DBs) for disaster recovery of the primary store.
  compose exec -T mongodb mongodump \
    --username "$MONGODB_USER" \
    --password "$MONGODB_PASSWORD" \
    --authenticationDatabase admin \
    --archive | gzip >"$dump_path"

  if [[ ! -s "$dump_path" ]]; then
    fail "MongoDB dump is empty: $dump_path"
  fi

  ln -sf "$(basename "$dump_path")" "$out_dir/proj_portfolio_mongo_latest.archive.gz"
  echo "$dump_path"
}

backup_postgres() {
  local stamp="$1"
  local out_dir="$BACKUP_DIR/postgres"
  local dump_path="$out_dir/proj_portfolio_${stamp}.dump.gz"
  mkdir -p "$out_dir"

  log "Backing up Postgres to $dump_path"
  compose_postgres exec -T db pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB" | gzip >"$dump_path"
  ln -sf "$(basename "$dump_path")" "$out_dir/proj_portfolio_latest.dump.gz"
  echo "$dump_path"
}

backup_redis() {
  local stamp="$1"
  local out_dir="$BACKUP_DIR/redis"
  local out_path="$out_dir/proj_portfolio_redis_${stamp}.rdb"
  mkdir -p "$out_dir"

  log "Backing up Redis to $out_path"
  compose exec -T redis redis-cli -a "$REDIS_PASSWORD" SAVE >/dev/null
  compose cp "redis:/data/dump.rdb" "$out_path"
  ln -sf "$(basename "$out_path")" "$out_dir/proj_portfolio_redis_latest.rdb"
}

backup_media() {
  local stamp="$1"
  local out_dir="$BACKUP_DIR/media"
  local out_path="$out_dir/proj_portfolio_media_${stamp}.tar.gz"
  mkdir -p "$out_dir"

  log "Backing up media volume to $out_path"
  compose run --rm --no-deps \
    -v server_media:/data:ro \
    -v "$out_dir:/out" \
    alpine:3.21 \
    sh -c "tar czf /out/proj_portfolio_media_${stamp}.tar.gz -C /data ."
  ln -sf "$(basename "$out_path")" "$out_dir/proj_portfolio_media_latest.tar.gz"
}

is_weekly_keeper() {
  local file_path="$1"
  local keep_weeks="$2"
  local file_date day_of_week cutoff_ts file_ts

  file_date="$(basename "$file_path" | sed -n 's/.*_\([0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}\)_.*/\1/p')"
  if [[ -z "$file_date" ]]; then
    return 1
  fi

  day_of_week="$(date -j -f "%Y-%m-%d" "$file_date" "+%u" 2>/dev/null || date -d "$file_date" "+%u")"
  if [[ "$day_of_week" != "7" ]]; then
    return 1
  fi

  file_ts="$(date -j -f "%Y-%m-%d" "$file_date" "+%s" 2>/dev/null || date -d "$file_date" "+%s")"
  cutoff_ts="$(date -v-"${keep_weeks}"w "+%s" 2>/dev/null || date -d "${keep_weeks} weeks ago" "+%s")"
  [[ "$file_ts" -ge "$cutoff_ts" ]]
}

rotate_dated_backups() {
  local dir="$1"
  local glob_pattern="$2"
  local latest_name="$3"
  local keep_days="$BACKUP_RETENTION_DAYS"
  local keep_weeks="$BACKUP_RETENTION_WEEKS"
  local file age_days

  shopt -s nullglob
  for file in "$dir"/$glob_pattern; do
    [[ "$(basename "$file")" == "$latest_name" ]] && continue
    age_days=$(( ( $(date +%s) - $(stat -f %m "$file" 2>/dev/null || stat -c %Y "$file") ) / 86400 ))
    if (( age_days <= keep_days )); then
      continue
    fi
    if is_weekly_keeper "$file" "$keep_weeks"; then
      continue
    fi
    log "Removing old backup: $file"
    rm -f "$file"
  done
  shopt -u nullglob
}

rotate_backups() {
  log "Rotating backups (keep ${BACKUP_RETENTION_DAYS} days, ${BACKUP_RETENTION_WEEKS} weekly Sunday copies)"
  rotate_dated_backups "$BACKUP_DIR/mongodb" "proj_portfolio_mongo_*.archive.gz" "proj_portfolio_mongo_latest.archive.gz"

  if postgres_enabled; then
    rotate_dated_backups "$BACKUP_DIR/postgres" "proj_portfolio_*.dump.gz" "proj_portfolio_latest.dump.gz"
  fi

  find "$BACKUP_DIR/redis" -name 'proj_portfolio_redis_*.rdb' -mtime +"$BACKUP_RETENTION_DAYS" ! -name 'proj_portfolio_redis_latest.rdb' -delete 2>/dev/null || true
  find "$BACKUP_DIR/media" -name 'proj_portfolio_media_*.tar.gz' -mtime +"$BACKUP_RETENTION_DAYS" ! -name 'proj_portfolio_media_latest.tar.gz' -delete 2>/dev/null || true
}

verify_mongodb_backup() {
  local dump_path="$1"
  log "Verifying MongoDB backup integrity (mongorestore --dryRun)"
  gunzip -c "$dump_path" | compose exec -T mongodb mongorestore \
    --username "$MONGODB_USER" \
    --password "$MONGODB_PASSWORD" \
    --authenticationDatabase admin \
    --archive \
    --dryRun \
    >/dev/null
}

verify_postgres_backup() {
  local dump_path="$1"
  log "Verifying Postgres backup integrity"
  gunzip -c "$dump_path" | compose_postgres exec -T db pg_restore --list >/dev/null
}

notify_result() {
  local status="$1"
  local detail="${2:-}"

  if [[ "$BACKUP_NOTIFY" != "true" ]]; then
    return 0
  fi

  if [[ -z "$(compose ps -q server 2>/dev/null || true)" ]]; then
    compose up -d server
  fi

  compose exec -T server python -m app.scripts.notify_backup_result "$status" "$detail" || true
}

# Optional offsite copy after local verify. Operator supplies the full command
# (e.g. rsync). Fail the run if it exits non-zero so Telegram notify sees failure.
run_offsite_backup() {
  if [[ -z "$BACKUP_OFFSITE_CMD" ]]; then
    return 0
  fi
  log "Running offsite backup: $BACKUP_OFFSITE_CMD"
  bash -c "$BACKUP_OFFSITE_CMD" || fail "offsite backup failed"
}

acquire_lock() {
  if command -v flock >/dev/null 2>&1; then
    exec 200>"${BACKUP_DIR}/.db_maintenance.flock"
    flock -n 200 || fail "db_maintenance already running"
    return 0
  fi
  if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    fail "db_maintenance already running (lock: $LOCK_DIR)"
  fi
}

release_lock() {
  if [[ -d "$LOCK_DIR" ]]; then
    rmdir "$LOCK_DIR" 2>/dev/null || true
  fi
}

main() {
  load_env
  mkdir -p "$BACKUP_DIR/mongodb" "$BACKUP_DIR/redis" "$BACKUP_DIR/media" logs
  if postgres_enabled; then
    mkdir -p "$BACKUP_DIR/postgres"
  fi

  acquire_lock
  trap release_lock EXIT

  local stamp mongo_dump_path pg_dump_path detail
  stamp="$(date +"%Y-%m-%d_%H%M")"
  detail="stamp=${stamp}"

  trap 'release_lock; notify_result failure "${detail:-unexpected error}"' ERR

  ensure_stack_ready
  run_migrate
  mongo_dump_path="$(backup_mongodb "$stamp")"
  if postgres_enabled; then
    pg_dump_path="$(backup_postgres "$stamp")"
  fi
  backup_redis "$stamp"
  backup_media "$stamp"
  rotate_backups
  verify_mongodb_backup "$mongo_dump_path"
  if postgres_enabled; then
    verify_postgres_backup "$pg_dump_path"
  fi
  run_offsite_backup

  log "DB maintenance completed successfully"
  notify_result success "$detail"
}

main "$@"
