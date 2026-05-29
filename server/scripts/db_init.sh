#!/bin/sh
# Wait for Postgres, run Alembic migrations, optionally seed. Used by migrate service and server entrypoint.
set -e

wait_for_db() {
    python - <<'PY'
import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.settings import get_settings

MAX_ATTEMPTS = 30


async def main() -> None:
    engine = create_async_engine(get_settings().DATABASE_URL, pool_pre_ping=True)
    try:
        for _ in range(MAX_ATTEMPTS):
            try:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                return
            except (OSError, Exception):
                await asyncio.sleep(1)
        print("database not ready after retries", file=sys.stderr)
        sys.exit(1)
    finally:
        await engine.dispose()


asyncio.run(main())
PY
}

echo "Waiting for database..."
wait_for_db

echo "Running database migrations..."
alembic upgrade head

if [ "$RUN_SEED" = "true" ]; then
    echo "Running database seed..."
    python -m app.db.seed
fi
