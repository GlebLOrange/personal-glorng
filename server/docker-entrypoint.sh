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

if python - <<'PY'
from app.settings import get_settings

if get_settings().RUN_MIGRATIONS:
    raise SystemExit(0)
raise SystemExit(1)
PY
then
    /app/scripts/db_init.sh
fi

exec "$@"
