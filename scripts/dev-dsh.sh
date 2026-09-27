#!/usr/bin/env bash
# Start/stop/status for DeepSeek Harness (DSH) web UI on the host.
# ponytail: host process only (needs Node + local Gortex); upgrade path is a compose sidecar.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

export DSH_HOME="${DSH_HOME:-$HOME/.dsh}"
pid_file="${DSH_HOME}/dev.pid"
log_file="${DSH_HOME}/dev.log"
port="${DSH_PORT:-3080}"
patch="ai/dsh/patch-gortex.yml"
# Cursor/agent shells sometimes set npm_config_devdir; that breaks npx for DSH.
unset npm_config_devdir NPM_CONFIG_DEVDIR 2>/dev/null || true

# --patch is a top-level launcher flag; `dsh web --patch` fails with unknown option.
dsh_cmd=(npx --yes @deepseek-ai/dsh --profile web --patch "$patch")

usage() {
  echo "Usage: $0 {start|stop|status|foreground}" >&2
  exit 2
}

port_listening() {
  lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

listener_pid() {
  lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null | head -1
}

load_deepseek_key() {
  if [ -n "${DEEPSEEK_API_KEY:-}" ]; then
    return 0
  fi
  if [ ! -f "$root/.env" ]; then
    return 0
  fi
  # ponytail: one-line grep; upgrade path is a proper dotenv parser if values need escapes.
  local line value
  line="$(grep -E '^DEEPSEEK_API_KEY=' "$root/.env" | head -1 || true)"
  if [ -z "$line" ]; then
    return 0
  fi
  value="${line#DEEPSEEK_API_KEY=}"
  value="${value%\"}"
  value="${value#\"}"
  value="${value%\'}"
  value="${value#\'}"
  export DEEPSEEK_API_KEY="$value"
}

warn_missing_key() {
  if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
    echo "dev-dsh: DEEPSEEK_API_KEY unset (UI still starts; chat needs the key in the environment or .env)" >&2
  fi
}

warn_gortex() {
  if ! command -v gortex >/dev/null 2>&1; then
    echo "dev-dsh: gortex not on PATH (mcp-gortex may fail until it is)" >&2
    return 0
  fi
  if ! gortex status >/dev/null 2>&1; then
    echo "dev-dsh: gortex daemon not ready (UI still starts; tools need \`gortex daemon start\`)" >&2
  fi
}

pid_alive() {
  local pid="$1"
  kill -0 "$pid" 2>/dev/null
}

kill_tree() {
  local pid="$1"
  local child
  for child in $(pgrep -P "$pid" 2>/dev/null || true); do
    kill_tree "$child"
  done
  kill "$pid" 2>/dev/null || true
}

cmd_status() {
  if port_listening; then
    echo "dsh: listening on 127.0.0.1:${port}"
    if [ -f "$pid_file" ]; then
      echo "dsh: pid $(cat "$pid_file") ($pid_file)"
    fi
    return 0
  fi
  echo "dsh: not listening on ${port}" >&2
  return 1
}

cmd_stop() {
  if [ ! -f "$pid_file" ]; then
    echo "dev-dsh: no pid file ($pid_file)"
    return 0
  fi
  local pid
  pid="$(cat "$pid_file")"
  if pid_alive "$pid"; then
    kill_tree "$pid"
    local i=0
    while pid_alive "$pid" && [ "$i" -lt 30 ]; do
      sleep 0.1
      i=$((i + 1))
    done
    if pid_alive "$pid"; then
      kill -9 "$pid" 2>/dev/null || true
    fi
    echo "dev-dsh: stopped pid $pid"
  else
    echo "dev-dsh: stale pid file (pid $pid not running)"
  fi
  rm -f "$pid_file"
}

cmd_start() {
  mkdir -p "$DSH_HOME"
  load_deepseek_key
  warn_missing_key
  warn_gortex

  if port_listening; then
    echo "dev-dsh: already listening on 127.0.0.1:${port} (leaving it alone)"
    return 0
  fi

  if [ -f "$pid_file" ]; then
    local old
    old="$(cat "$pid_file")"
    if pid_alive "$old"; then
      echo "dev-dsh: process $old still running but port ${port} is free; stopping leftover" >&2
      kill_tree "$old"
    fi
    rm -f "$pid_file"
  fi

  # Truncate log for this boot so failures are easy to spot.
  : >"$log_file"

  # nohup so make/docker compose foreground does not kill DSH when the shell exits.
  # --no-open: make/dev background must not steal focus with a browser tab.
  nohup "${dsh_cmd[@]}" --no-open >>"$log_file" 2>&1 &
  local launcher_pid=$!
  echo "$launcher_pid" >"$pid_file"

  # npx cold-start often needs 15–30s before :3080 listens.
  local i=0
  while [ "$i" -lt 90 ]; do
    if port_listening; then
      local listen_pid
      listen_pid="$(listener_pid)"
      if [ -n "$listen_pid" ]; then
        echo "$listen_pid" >"$pid_file"
      fi
      echo "dev-dsh: started pid $(cat "$pid_file") → http://127.0.0.1:${port} (log: $log_file)"
      return 0
    fi
    if ! pid_alive "$launcher_pid"; then
      # Launcher may exit after spawning node; only fail once nothing is left.
      if [ "$i" -gt 20 ] && ! port_listening; then
        if ! pgrep -f '@deepseek-ai/dsh|lib/bin.js' >/dev/null 2>&1; then
          echo "dev-dsh: process exited before listen; see $log_file" >&2
          rm -f "$pid_file"
          return 1
        fi
      fi
    fi
    sleep 0.5
    i=$((i + 1))
  done

  echo "dev-dsh: started launcher pid $launcher_pid but port ${port} not open yet; see $log_file" >&2
  return 0
}

cmd_foreground() {
  mkdir -p "$DSH_HOME"
  load_deepseek_key
  warn_missing_key
  warn_gortex
  exec "${dsh_cmd[@]}"
}

case "${1:-}" in
  start) cmd_start ;;
  stop) cmd_stop ;;
  status) cmd_status ;;
  foreground) cmd_foreground ;;
  *) usage ;;
esac
