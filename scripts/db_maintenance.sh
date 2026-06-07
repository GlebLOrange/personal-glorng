#!/usr/bin/env bash
# Daily DB maintenance: migrate, backup Postgres/Redis/media, rotate, verify, notify.
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

load_env() {
  if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
  fi

  : "${POSTGRES_USER:?POSTGRES_USER is required}"
  : "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
  : "${POSTGRES_DB:?POSTGRES_DB is required}"
  : "${REDIS_PASSWORD:?REDIS_PASSWORD is required}"

  BACKUP_DIR="${BACKUP_DIR:-./backups}"
  BACKUP_COMPOSE_FILE="${BACKUP_COMPOSE_FILE:-docker-compose.prod.yml}"
  BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
  BACKUP_RETENTION_WEEKS="${BACKUP_RETENTION_WEEKS:-4}"
  BACKUP_NOTIFY="${BACKUP_NOTIFY:-true}"
  LOCK_DIR="${BACKUP_DIR}/.db_maintenance.lock.d"
}

compose() {
  docker compose -f "$BACKUP_COMPOSE_FILE" "$@"
}

ensure_stack_ready() {
  compose up -d db redis
  compose exec -T db pg_isready -U "$POSTGRES_USER" >/dev/null
}

run_migrate() {
  log "Running Alembic migrations"
  compose run --rm migrate
}

backup_postgres() {
  local stamp="$1"
  local out_dir="$BACKUP_DIR/postgres"
  local dump_path="$out_dir/glorng_${stamp}.dump.gz"
  mkdir -p "$out_dir"

  log "Backing up Postgres to $dump_path"
  compose exec -T db pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB" | gzip >"$dump_path"
  ln -sf "$(basename "$dump_path")" "$out_dir/glorng_latest.dump.gz"
  echo "$dump_path"
}

backup_redis() {
  local stamp="$1"
  local out_dir="$BACKUP_DIR/redis"
  local out_path="$out_dir/glorng_redis_${stamp}.rdb"
  mkdir -p "$out_dir"

  log "Backing up Redis to $out_path"
  compose exec -T redis redis-cli -a "$REDIS_PASSWORD" SAVE >/dev/null
  compose cp "redis:/data/dump.rdb" "$out_path"
  ln -sf "$(basename "$out_path")" "$out_dir/glorng_redis_latest.rdb"
}

backup_media() {
  local stamp="$1"
  local out_dir="$BACKUP_DIR/media"
  local out_path="$out_dir/glorng_media_${stamp}.tar.gz"
  mkdir -p "$out_dir"

  log "Backing up media volume to $out_path"
  compose run --rm --no-deps \
    -v server_media:/data:ro \
    -v "$out_dir:/out" \
    alpine:3.21 \
    sh -c "tar czf /out/glorng_media_${stamp}.tar.gz -C /data ."
  ln -sf "$(basename "$out_path")" "$out_dir/glorng_media_latest.tar.gz"
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

rotate_backups() {
  local dir="$BACKUP_DIR/postgres"
  local keep_days="$BACKUP_RETENTION_DAYS"
  local keep_weeks="$BACKUP_RETENTION_WEEKS"
  local file age_days

  log "Rotating backups (keep ${keep_days} days, ${keep_weeks} weekly Sunday copies)"
  shopt -s nullglob
  for file in "$dir"/glorng_*.dump.gz; do
    [[ "$(basename "$file")" == "glorng_latest.dump.gz" ]] && continue
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

  find "$BACKUP_DIR/redis" -name 'glorng_redis_*.rdb' -mtime +"$keep_days" ! -name 'glorng_redis_latest.rdb' -delete 2>/dev/null || true
  find "$BACKUP_DIR/media" -name 'glorng_media_*.tar.gz' -mtime +"$keep_days" ! -name 'glorng_media_latest.tar.gz' -delete 2>/dev/null || true
}

verify_postgres_backup() {
  local dump_path="$1"
  log "Verifying Postgres backup integrity"
  gunzip -c "$dump_path" | compose exec -T db pg_restore --list >/dev/null
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
  mkdir -p "$BACKUP_DIR/postgres" "$BACKUP_DIR/redis" "$BACKUP_DIR/media" logs

  acquire_lock
  trap release_lock EXIT

  local stamp dump_path detail
  stamp="$(date +"%Y-%m-%d_%H%M")"
  detail="stamp=${stamp}"

  trap 'release_lock; notify_result failure "${detail:-unexpected error}"' ERR

  ensure_stack_ready
  run_migrate
  dump_path="$(backup_postgres "$stamp")"
  backup_redis "$stamp"
  backup_media "$stamp"
  rotate_backups
  verify_postgres_backup "$dump_path"

  log "DB maintenance completed successfully"
  notify_result success "$detail"
}

main "$@"
