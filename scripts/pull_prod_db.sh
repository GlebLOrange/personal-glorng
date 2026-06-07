#!/usr/bin/env bash
# Pull a prod Postgres backup into local dev. Manual use only — never schedule on prod.
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

if [[ "${CONFIRM_PROD_PULL:-}" != "1" ]]; then
  fail "Set CONFIRM_PROD_PULL=1 to overwrite local dev data with prod"
fi

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"

LOCAL_COMPOSE_FILE="${LOCAL_COMPOSE_FILE:-docker-compose.yml}"
PROD_BACKUP_PATH="${PROD_BACKUP_PATH:-}"
PROD_SSH_HOST="${PROD_SSH_HOST:-}"
PROD_BACKUP_DIR="${PROD_BACKUP_DIR:-./backups/postgres/glorng_latest.dump.gz}"
TMP_DUMP="$(mktemp "${TMPDIR:-/tmp}/glorng_prod_pull.XXXXXX.dump.gz")"

cleanup() {
  rm -f "$TMP_DUMP"
}
trap cleanup EXIT

compose_local() {
  docker compose -f "$LOCAL_COMPOSE_FILE" "$@"
}

fetch_backup() {
  if [[ -n "$PROD_BACKUP_PATH" ]]; then
    log "Using local prod backup: $PROD_BACKUP_PATH"
    cp "$PROD_BACKUP_PATH" "$TMP_DUMP"
    return 0
  fi

  if [[ -n "$PROD_SSH_HOST" ]]; then
    log "Fetching backup from $PROD_SSH_HOST:$PROD_BACKUP_DIR"
    scp "${PROD_SSH_HOST}:${PROD_BACKUP_DIR}" "$TMP_DUMP"
    return 0
  fi

  fail "Set PROD_BACKUP_PATH or PROD_SSH_HOST (remote path: PROD_BACKUP_DIR)"
}

restore_backup() {
  log "Starting local db service"
  compose_local up -d db
  compose_local exec -T db pg_isready -U "$POSTGRES_USER" >/dev/null

  log "Restoring prod dump into local ${POSTGRES_DB}"
  gunzip -c "$TMP_DUMP" | compose_local exec -T db pg_restore \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --clean \
    --if-exists \
    --no-owner \
    --role="$POSTGRES_USER"

  log "Local dev database restored from prod backup"
}

fetch_backup
restore_backup
