"""Shared MongoDB repository helpers."""

from datetime import UTC, datetime
from typing import Any, TypeVar

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.core.exceptions import NotFoundError
from app.db.documents.base import TimestampedDocument, document_to_dict, utc_now
from app.db.mongo.counter import next_sequence_id

DocT = TypeVar("DocT", bound=TimestampedDocument)


def _parse_doc(model: type[DocT], data: dict[str, Any]) -> DocT:
    payload = dict(data)
    payload.pop("_id", None)
    return model.model_validate(payload)


class MongoRepository[DocT: TimestampedDocument]:
    """Generic CRUD repository for timestamped Pydantic documents."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        collection: str,
        model: type[DocT],
        *,
        counter_name: str | None = None,
    ) -> None:
        self.db = db
        self.collection = collection
        self.model = model
        self.counter_name = counter_name or collection

    def _col(self):
        return self.db[self.collection]

    async def next_id(self) -> int:
        return await next_sequence_id(self.db, self.counter_name)

    async def get(self, doc_id: int) -> DocT:
        row = await self.get_or_none(doc_id)
        if row is None:
            raise NotFoundError(f"Resource with id {doc_id} not found")
        return row

    async def get_or_none(self, doc_id: int) -> DocT | None:
        data = await self._col().find_one({"id": doc_id})
        if data is None:
            return None
        return _parse_doc(self.model, data)

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        sort: list[tuple[str, int]] | None = None,
        **filters: Any,
    ) -> list[DocT]:
        query = {k: v for k, v in filters.items() if v is not None}
        cursor = self._col().find(query).skip(offset).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        return [_parse_doc(self.model, row) async for row in cursor]

    async def count(self, **filters: Any) -> int:
        query = {k: v for k, v in filters.items() if v is not None}
        return await self._col().count_documents(query)

    async def insert(self, doc: DocT) -> DocT:
        now = utc_now()
        if doc.id == 0:
            doc.id = await self.next_id()
        doc.created_at = doc.created_at or now
        doc.updated_at = now
        await self._col().insert_one(document_to_dict(doc))
        return doc

    async def update_fields(self, doc_id: int, **fields: Any) -> DocT:
        fields["updated_at"] = datetime.now(UTC)
        result = await self._col().find_one_and_update(
            {"id": doc_id},
            {"$set": fields},
            return_document=True,
        )
        if result is None:
            raise NotFoundError(f"Resource with id {doc_id} not found")
        return _parse_doc(self.model, result)

    async def replace(self, doc: DocT) -> DocT:
        doc.updated_at = datetime.now(UTC)
        result = await self._col().replace_one(
            {"id": doc.id},
            document_to_dict(doc),
        )
        if result.matched_count == 0:
            raise NotFoundError(f"Resource with id {doc.id} not found")
        return doc

    async def delete(self, doc_id: int) -> None:
        result = await self._col().delete_one({"id": doc_id})
        if result.deleted_count == 0:
            raise NotFoundError(f"Resource with id {doc_id} not found")
