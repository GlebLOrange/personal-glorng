"""MongoDB repository for staged data imports."""

from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.base import document_to_dict, utc_now
from app.db.documents.import_batch import ImportBatch
from app.db.documents.import_row import ImportRow
from app.db.mongo.counter import next_sequence_ids
from app.db.repositories.base import MongoRepository, _parse_doc

BULK_INSERT_SIZE = 500


class ImportBatchRepository(MongoRepository[ImportBatch]):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "import_batches", ImportBatch)

    async def list_for_user(
        self,
        imported_by: int,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[ImportBatch]:
        return await self.list(
            offset=offset,
            limit=limit,
            imported_by=imported_by,
            sort=[("created_at", -1)],
        )

    async def count_for_user(self, imported_by: int) -> int:
        return await self.count(imported_by=imported_by)


class ImportRowRepository(MongoRepository[ImportRow]):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "import_rows", ImportRow)

    async def insert_many(self, rows: list[ImportRow]) -> None:
        if not rows:
            return
        now = utc_now()
        pending = [row for row in rows if row.id == 0]
        if pending:
            ids = await next_sequence_ids(self.db, self.counter_name, len(pending))
            for row, row_id in zip(pending, ids, strict=True):
                row.id = row_id
        docs: list[dict[str, Any]] = []
        for row in rows:
            row.created_at = row.created_at or now
            row.updated_at = now
            docs.append(document_to_dict(row))
            if len(docs) >= BULK_INSERT_SIZE:
                await self._col().insert_many(docs)
                docs = []
        if docs:
            await self._col().insert_many(docs)

    async def delete_for_batch(self, batch_id: int) -> None:
        await self._col().delete_many({"batch_id": batch_id})

    async def list_for_batch(
        self,
        batch_id: int,
        *,
        limit: int = 50,
        offset: int = 0,
        errors_only: bool = False,
    ) -> list[ImportRow]:
        query: dict[str, Any] = {"batch_id": batch_id}
        if errors_only:
            query["error"] = {"$ne": None}
        cursor = self._col().find(query).sort("row_index", 1).skip(offset).limit(limit)
        return [_parse_doc(ImportRow, row) async for row in cursor]

    async def list_success_for_batch(
        self,
        batch_id: int,
        *,
        after_row_index: int | None = None,
        limit: int = 500,
    ) -> list[ImportRow]:
        query: dict[str, Any] = {"batch_id": batch_id, "error": None}
        if after_row_index is not None:
            query["row_index"] = {"$gt": after_row_index}
        cursor = self._col().find(query).sort("row_index", 1).limit(limit)
        return [_parse_doc(ImportRow, row) async for row in cursor]


class DataImportRepository:
    """Facade for import batch and row persistence."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.batches = ImportBatchRepository(db)
        self.rows = ImportRowRepository(db)

    async def delete_batch(self, batch_id: int) -> None:
        await self.rows.delete_for_batch(batch_id)
        await self.batches.delete(batch_id)
