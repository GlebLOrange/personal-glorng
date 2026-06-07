#!/bin/sh
set -e

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

if [ "$RUN_MIGRATIONS" = "true" ]; then
    /app/scripts/db_init.sh
fi

exec "$@"
