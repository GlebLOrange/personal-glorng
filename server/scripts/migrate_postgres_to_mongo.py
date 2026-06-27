#!/usr/bin/env python3
"""One-time migration: copy core Postgres tables into MongoDB collections."""

from __future__ import annotations

import asyncio
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.logging import logger
from app.db.mongo.migrate import ensure_mongo_schema
from app.settings import get_settings

_COLLECTIONS = (
    "users",
    "tasks",
    "task_status_history",
    "reminders",
    "task_intakes",
    "google_sync_queue",
    "recipes",
    "expenses",
    "expense_categories",
    "shortened_urls",
    "shared_files",
    "feedback",
    "github_credentials",
    "google_credentials",
    "weather_locations",
    "telegram_inbound_messages",
)


def _serialize(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value
    if isinstance(value, Decimal):
        return value
    if isinstance(value, uuid.UUID):
        return value
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if hasattr(value, "value"):
        return value.value
    return value


def _row_to_doc(row: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for col in row.__table__.columns:
        name = col.name
        if name == "metadata":
            data["metadata"] = getattr(row, "metadata_", None)
            continue
        data[name] = _serialize(getattr(row, col.key))
    return data


async def _copy_table(
    session: AsyncSession,
    mongo_db,
    model: type,
    *,
    collection: str | None = None,
) -> int:
    coll_name = collection or model.__tablename__
    result = await session.execute(select(model))
    rows = list(result.scalars().all())
    if not rows:
        return 0
    docs = [_row_to_doc(row) for row in rows]
    await mongo_db[coll_name].delete_many({})
    await mongo_db[coll_name].insert_many(docs)
    return len(docs)


async def migrate() -> None:
    settings = get_settings()
    if not settings.MONGODB_URL.strip():
        msg = "MONGODB_URL is required for migration"
        raise RuntimeError(msg)
    if not settings.DATABASE_URL.strip():
        msg = "DATABASE_URL is required (source Postgres)"
        raise RuntimeError(msg)

    from app.db.models import (
        Expense,
        ExpenseCategory,
        Feedback,
        GitHubCredential,
        GoogleCredential,
        GoogleSyncQueue,
        Recipe,
        Reminder,
        SharedFile,
        ShortenedUrl,
        Task,
        TaskIntake,
        TaskStatusHistory,
        TelegramInboundMessage,
        User,
        WeatherLocation,
    )

    mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongo_db = mongo_client[settings.MONGODB_DB]
    pg_engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(pg_engine, class_=AsyncSession)

    try:
        await ensure_mongo_schema(mongo_db)
        async with session_factory() as session:
            tables = [
                (User, "users"),
                (Task, "tasks"),
                (TaskStatusHistory, "task_status_history"),
                (Reminder, "reminders"),
                (TaskIntake, "task_intakes"),
                (GoogleSyncQueue, "google_sync_queue"),
                (Recipe, "recipes"),
                (Expense, "expenses"),
                (ExpenseCategory, "expense_categories"),
                (ShortenedUrl, "shortened_urls"),
                (SharedFile, "shared_files"),
                (Feedback, "feedback"),
                (GitHubCredential, "github_credentials"),
                (GoogleCredential, "google_credentials"),
                (WeatherLocation, "weather_locations"),
                (TelegramInboundMessage, "telegram_inbound_messages"),
            ]
            for model, coll in tables:
                count = await _copy_table(session, mongo_db, model, collection=coll)
                logger.info(
                    "Migrated collection",
                    context={"collection": coll, "documents": count},
                )

            max_id = 0
            for coll in _COLLECTIONS:
                doc = await mongo_db[coll].find_one(sort=[("id", -1)])
                if doc and doc.get("id", 0) > max_id:
                    max_id = doc["id"]
            await mongo_db.counters.update_one(
                {"_id": "global"},
                {"$set": {"seq": max_id}},
                upsert=True,
            )
            logger.info("Counter seeded", context={"max_id": max_id})
    finally:
        mongo_client.close()
        await pg_engine.dispose()


def main() -> None:
    asyncio.run(migrate())


if __name__ == "__main__":
    main()
