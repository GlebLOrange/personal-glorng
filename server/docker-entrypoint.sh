#!/bin/sh
set -e

if [ "$RUN_MIGRATIONS" = "true" ]; then
    /app/scripts/db_init.sh
fi

exec "$@"
