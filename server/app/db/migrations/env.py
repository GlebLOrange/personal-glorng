import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import JSON, pool
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.sql.schema import Column

_server_root = Path(__file__).resolve().parents[3]
if str(_server_root) not in sys.path:
    sys.path.insert(0, str(_server_root))

from app.db.models import Base
from app.db.recipe_search import RECIPE_SEARCH_INDEX
from app.db.search_index import SEARCH_INDEX_NAME
from app.settings import get_settings

_FTS_INDEX_NAMES = frozenset({RECIPE_SEARCH_INDEX, SEARCH_INDEX_NAME})


def include_object(
    _object: object,
    name: str | None,
    type_: str,
    _reflected: bool,
    _compare_to: object | None,
) -> bool:
    """Skip GIN FTS indexes; Postgres normalizes expressions and causes false drift."""
    return not (type_ == "index" and name in _FTS_INDEX_NAMES)


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def _is_json_column(column_type: object) -> bool:
    if isinstance(column_type, (JSON, JSONB)):
        return True
    impl = getattr(column_type, "impl", None)
    return isinstance(impl, (JSON, JSONB))


def compare_server_default(
    _context: object,
    _inspected_column: object,
    metadata_column: Column[object],
    _inspected_default: object | None,
    _metadata_default: object | None,
    _rendered_metadata_default: str | None,
) -> bool | None:
    """Skip JSON default compares that Postgres cannot evaluate (`json = unknown`)."""
    if _is_json_column(metadata_column.type):
        return False
    return None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=compare_server_default,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):  # type: ignore[no-untyped-def]
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=compare_server_default,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
