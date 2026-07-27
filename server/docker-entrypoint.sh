#!/bin/sh
set -e

# Load a KEY=value from GLORNG_ENV_FILE when the process env is unset.
# Compose mounts .env as GLORNG_ENV_FILE rather than injecting every key.
_env_file_get() {
    key="$1"
    if [ -z "${GLORNG_ENV_FILE:-}" ] || [ ! -f "$GLORNG_ENV_FILE" ]; then
        return 0
    fi
    # shellcheck disable=SC2002
    line=$(grep -E "^${key}=" "$GLORNG_ENV_FILE" | tail -n 1 || true)
    if [ -z "$line" ]; then
        return 0
    fi
    printf '%s\n' "${line#*=}" | tr -d '"' | tr -d "'"
}

_export_otel_from_env_file() {
    for key in \
        OTEL_SERVICE_NAME \
        OTEL_EXPORTER_OTLP_ENDPOINT \
        OTEL_EXPORTER_OTLP_HEADERS \
        OTEL_RESOURCE_ATTRIBUTES
    do
        eval "current=\${$key:-}"
        if [ -n "$current" ]; then
            continue
        fi
        value=$(_env_file_get "$key")
        if [ -n "$value" ]; then
            export "$key=$value"
        fi
    done
}

if command -v uv >/dev/null 2>&1 && [ -f /app/pyproject.toml ] && [ -f /app/uv.lock ]; then
    stamp=/app/.venv/.deps-synced
    if [ ! -x /app/.venv/bin/python ] \
        || [ ! -f "$stamp" ] \
        || [ /app/uv.lock -nt "$stamp" ] \
        || [ /app/pyproject.toml -nt "$stamp" ]; then
        uv sync --frozen --no-dev
        touch "$stamp"
    fi
fi

_export_otel_from_env_file

# Install auto-instrumentation packages when EDOT is enabled (and after uv sync).
# uv venvs omit pip; edot-bootstrap shells out to `python -m pip`.
if [ -n "${OTEL_EXPORTER_OTLP_ENDPOINT:-}" ] \
    && [ -x /app/.venv/bin/edot-bootstrap ]; then
    if ! /app/.venv/bin/python -m pip --version >/dev/null 2>&1; then
        uv pip install pip
    fi
    /app/.venv/bin/edot-bootstrap --action=install
fi

if python - <<'PY'
from app.settings import get_settings

if get_settings().RUN_MIGRATIONS:
    raise SystemExit(0)
raise SystemExit(1)
PY
then
    /app/scripts/db_init.sh
fi

# Opt-in EDOT: wrap only when an OTLP endpoint is configured.
# Do not set OTEL_TRACES_EXPORTER / METRICS / LOGS — EDOT defaults are correct.
# Never run classic elastic-apm alongside EDOT.
if [ -n "${OTEL_EXPORTER_OTLP_ENDPOINT:-}" ] \
    && command -v opentelemetry-instrument >/dev/null 2>&1; then
    exec opentelemetry-instrument "$@"
fi

exec "$@"
