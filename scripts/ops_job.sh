#!/usr/bin/env bash
# Hand-run ops jobs. Scheduling is out of scope — call from Make or later cron.
# Usage: scripts/ops_job.sh <job> | scripts/ops_job.sh --self-check
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

COMPOSE_CACHE="-f docker-compose.cache.yml"
COMPOSE_LITE="-f docker-compose.yml -f docker-compose.lite.yml ${COMPOSE_CACHE}"
COMPOSE_PROD="-f docker-compose.prod.yml ${COMPOSE_CACHE}"
LITE_SERVICES="mongodb redis redis-cache server nginx"
OPS_STACK="${OPS_STACK:-lite}"

# Safe prune list for docker-maintain. Self-check rejects volume / system / -a.
PRUNE_COMMANDS=(
  "docker container prune -f"
  "docker image prune -f"
  "docker builder prune -f"
)

log() {
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*" >&2
}

fail() {
  log "ERROR: $*"
  exit 1
}

print_menu() {
  cat <<'EOF' >&2
Usage: scripts/ops_job.sh <job>

Jobs:
  backup           make backup / db_maintenance.sh (dump + verify + rotate + migrate)
  maintenance      db_maintenance.sh --check-stale (freshness only)
  sync             drain Google Calendar sync queue (one batch, max 10)
  cleanup          old tasks + expired shares + health results
  logs-rotate      truncate Docker json-file logs for the selected stack
  docker-maintain  prune stopped containers, dangling images, build cache
  update           compose pull + up -d --build (OPS_STACK=lite|prod)

Also: scripts/ops_job.sh --self-check
EOF
}

compose_args() {
  case "$OPS_STACK" in
    lite) printf '%s' "$COMPOSE_LITE" ;;
    prod) printf '%s' "$COMPOSE_PROD" ;;
    *) fail "OPS_STACK must be lite or prod (got: $OPS_STACK)" ;;
  esac
}

run_server_job() {
  local job="$1"
  # shellcheck disable=SC2086
  docker compose $COMPOSE_LITE exec -T server python -m app.scripts.run_ops_job "$job"
}

run_backup() {
  bash "$root/scripts/db_maintenance.sh"
}

run_maintenance() {
  bash "$root/scripts/db_maintenance.sh" --check-stale
}

run_logs_rotate() {
  local args id log_path truncated=0 skipped=0
  args="$(compose_args)"
  # shellcheck disable=SC2086
  while IFS= read -r id; do
    [[ -n "$id" ]] || continue
    log_path="$(docker inspect --format='{{.LogPath}}' "$id" 2>/dev/null || true)"
    if [[ -z "$log_path" || ! -e "$log_path" ]]; then
      log "skip $id (no LogPath)"
      skipped=$((skipped + 1))
      continue
    fi
    if : >"$log_path" 2>/dev/null; then
      log "truncated $log_path"
      truncated=$((truncated + 1))
    else
      log "WARNING: cannot truncate $log_path (permission?)"
      skipped=$((skipped + 1))
    fi
  done < <(docker compose $args ps -q)
  log "logs-rotate done truncated=${truncated} skipped=${skipped}"
}

run_docker_maintain() {
  local cmd
  for cmd in "${PRUNE_COMMANDS[@]}"; do
    log "Running: $cmd"
    # shellcheck disable=SC2086
    $cmd
  done
  log "docker-maintain done"
}

run_update() {
  local args
  args="$(compose_args)"
  log "update OPS_STACK=${OPS_STACK}"
  # shellcheck disable=SC2086
  docker compose $args pull
  if [[ "$OPS_STACK" == "lite" ]]; then
    # shellcheck disable=SC2086
    DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 \
      docker compose $args up -d --build $LITE_SERVICES
  else
    # shellcheck disable=SC2086
    DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 \
      docker compose $args up -d --build
  fi
  log "update done"
}

self_check() {
  local joined cmd
  joined="$(printf '%s\n' "${PRUNE_COMMANDS[@]}")"
  if printf '%s\n' "$joined" | grep -Eiq '(^|[[:space:]])volume([[:space:]]|$)|system[[:space:]]+prune|image[[:space:]]+prune[[:space:]]+-a'; then
    fail "self-check: prune list must not include volume, system prune, or image prune -a"
  fi
  for cmd in "${PRUNE_COMMANDS[@]}"; do
    case "$cmd" in
      "docker container prune -f"|"docker image prune -f"|"docker builder prune -f") ;;
      *) fail "self-check: unexpected prune command: $cmd" ;;
    esac
  done
  [[ -f "$root/scripts/db_maintenance.sh" ]] || fail "self-check: db_maintenance.sh missing"
  [[ -f "$root/server/app/scripts/run_ops_job.py" ]] || fail "self-check: run_ops_job.py missing"
  log "self-check ok"
}

main() {
  local job="${1:-}"
  case "$job" in
    --self-check)
      self_check
      ;;
    backup)
      run_backup
      ;;
    maintenance)
      run_maintenance
      ;;
    sync)
      run_server_job sync
      ;;
    cleanup)
      run_server_job cleanup
      ;;
    logs-rotate)
      run_logs_rotate
      ;;
    docker-maintain)
      run_docker_maintain
      ;;
    update)
      run_update
      ;;
    ""|-h|--help)
      print_menu
      exit 1
      ;;
    *)
      print_menu
      fail "unknown job: $job"
      ;;
  esac
}

main "$@"
