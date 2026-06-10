#!/bin/sh
# Wait for enabled databases, run migrations, optionally seed.
set -e

wait_for_mongo() {
    python - <<'PY'
import asyncio
import sys

from motor.motor_asyncio import AsyncIOMotorClient

from app.settings import get_settings

MAX_ATTEMPTS = 30


async def main() -> None:
    settings = get_settings()
    if not settings.enable_mongodb():
        return
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    try:
        for _ in range(MAX_ATTEMPTS):
            try:
                await client.admin.command("ping")
                return
            except (OSError, Exception):
                await asyncio.sleep(1)
        print("mongodb not ready after retries", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


asyncio.run(main())
PY
}

wait_for_postgres() {
    python - <<'PY'
import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.settings import get_settings

MAX_ATTEMPTS = 30


async def main() -> None:
    settings = get_settings()
    if not settings.enable_postgres():
        return
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    try:
        for _ in range(MAX_ATTEMPTS):
            try:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                return
            except (OSError, Exception):
                await asyncio.sleep(1)
        print("postgres not ready after retries", file=sys.stderr)
        sys.exit(1)
    finally:
        await engine.dispose()


asyncio.run(main())
PY
}

echo "Waiting for MongoDB..."
wait_for_mongo

echo "Running MongoDB schema setup..."
python -m app.db.mongo.migrate

if [ "$(python - <<'PY'
from app.settings import get_settings
print("true" if get_settings().enable_postgres() else "false")
PY
)" = "true" ]; then
    echo "Waiting for PostgreSQL..."
    wait_for_postgres
    echo "Running PostgreSQL migrations..."
    alembic upgrade head
fi

if python - <<'PY'
from app.settings import get_settings

if get_settings().RUN_SEED:
    raise SystemExit(0)
raise SystemExit(1)
PY
then
    echo "Running demo database seed..."
    count="$(python - <<'PY'
from app.settings import get_settings

print(get_settings().SEED_DEMO_COUNT)
PY
)"
    python -m app.db.seed_demo \
        --count "$count" \
        --no-reset \
        --skip-if-populated
fi
