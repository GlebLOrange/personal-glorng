import re
from datetime import date, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.app_log import AppLog
from app.db.mongo.counter import next_sequence_ids


def _from_doc(data: dict[str, Any]) -> AppLog:
    payload = dict(data)
    payload.pop("_id", None)
    return AppLog(
        id=payload["id"],
        occurred_at=payload.get("occurred_at"),
        level=payload["level"],
        message=payload["message"],
        logger=payload.get("logger", "glorng"),
        context=payload.get("context"),
        error=payload.get("error"),
        error_type=payload.get("error_type"),
        traceback=payload.get("traceback"),
        request_id=payload.get("request_id"),
    )


class AppLogRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db

    async def insert_many(self, entries: list[AppLog]) -> None:
        if not entries:
            return
        missing = [entry for entry in entries if not entry.id]
        if missing:
            ids = await next_sequence_ids(self.db, "app_logs", len(missing))
            for entry, entry_id in zip(missing, ids, strict=True):
                entry.id = entry_id
        docs: list[dict[str, Any]] = []
        for entry in entries:
            docs.append(
                {
                    "id": entry.id,
                    "occurred_at": entry.occurred_at,
                    "level": entry.level,
                    "message": entry.message,
                    "logger": entry.logger,
                    "context": entry.context,
                    "error": entry.error,
                    "error_type": entry.error_type,
                    "traceback": entry.traceback,
                    "request_id": entry.request_id,
                },
            )
        await self.db.app_logs.insert_many(docs)

    async def list_events(
        self,
        *,
        level: str | None = None,
        request_id: str | None = None,
        message: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[AppLog], int]:
        query: dict[str, Any] = {}
        if level:
            query["level"] = level.lower()
        if request_id:
            query["request_id"] = request_id.strip()
        if message:
            query["message"] = {
                "$regex": re.escape(message.strip()),
                "$options": "i",
            }
        if date_from or date_to:
            occurred: dict[str, datetime] = {}
            if date_from:
                occurred["$gte"] = datetime.combine(date_from, datetime.min.time())
            if date_to:
                occurred["$lte"] = datetime.combine(date_to, datetime.max.time())
            query["occurred_at"] = occurred

        total = await self.db.app_logs.count_documents(query)
        cursor = (
            self.db.app_logs.find(query)
            .sort("occurred_at", -1)
            .skip(offset)
            .limit(limit)
        )
        items = [_from_doc(row) async for row in cursor]
        return items, total
