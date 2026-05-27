from typing import Any, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDService[ModelType: Base]:
    def __init__(self, db: AsyncSession, model: type[ModelType]) -> None:
        self.db = db
        self.model = model

    async def get(self, id: int) -> ModelType:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise NotFoundError(f"Resource with id {id} not found")
        return obj

    async def get_or_none(self, id: int) -> ModelType | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        offset: int = 0,
        limit: int = 20,
        **filters: Any,  # noqa: ANN401
    ) -> list[ModelType]:
        query = select(self.model).offset(offset).limit(limit)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        **filters: Any,  # noqa: ANN401
    ) -> int:
        query = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def create(self, data: dict[str, Any]) -> ModelType:
        obj = self.model(**data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: int) -> None:
        obj = await self.get(id)
        await self.db.delete(obj)
        await self.db.flush()
