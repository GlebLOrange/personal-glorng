#!/bin/sh
set -e

if [ ! -x /app/.venv/bin/python ]; then
    uv sync --frozen --no-dev
fi

if [ "$RUN_MIGRATIONS" = "true" ]; then
    /app/scripts/db_init.sh
fi

exec "$@"
