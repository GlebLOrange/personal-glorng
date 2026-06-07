from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApiError, NotFoundError
from app.core.utils import generate_short_code
from app.db.models.url import ShortenedUrl
from app.services.audit import AuditService
from app.services.base import CRUDService
from app.services.search_indexers.url import index_url, remove_url

_MAX_CODE_RETRIES = 3


class UrlService(CRUDService[ShortenedUrl]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, ShortenedUrl)

    async def create_short_url(
        self,
        original_url: str,
        created_by: int | None,
        title: str | None = None,
    ) -> ShortenedUrl:
        for attempt in range(_MAX_CODE_RETRIES):
            code = generate_short_code(8)
            try:
                url = await self.create(
                    {
                        "code": code,
                        "original_url": original_url,
                        "title": title,
                        "created_by": created_by,
                    }
                )
                await index_url(self.db, url)
                await AuditService(self.db).record_domain(
                    action="url.created",
                    resource_type="url",
                    resource_id=url.id,
                    actor_id=created_by,
                    metadata={"code": url.code},
                )
                return url
            except IntegrityError:
                await self.db.rollback()
                if attempt == _MAX_CODE_RETRIES - 1:
                    raise ApiError(
                        503, "Failed to generate unique short code"
                    ) from None
        raise ApiError(503, "Failed to generate unique short code")

    async def get_by_code(self, code: str) -> ShortenedUrl:
        result = await self.db.execute(
            select(ShortenedUrl).where(ShortenedUrl.code == code)
        )
        url = result.scalar_one_or_none()
        if not url:
            raise NotFoundError(f"URL with code '{code}' not found")
        return url

    async def increment_clicks(self, code: str) -> None:
        await self.db.execute(
            update(ShortenedUrl)
            .where(ShortenedUrl.code == code)
            .values(clicks=ShortenedUrl.clicks + 1)
        )
        await self.db.flush()

    async def list_by_owner(
        self,
        created_by: int,
        offset: int = 0,
        limit: int = 20,
    ) -> list[ShortenedUrl]:
        return await self.list(offset=offset, limit=limit, created_by=created_by)

    async def delete_url(
        self,
        url_id: int,
        actor_id: int,
        *,
        is_superuser: bool = False,
    ) -> None:
        url = await self.get(url_id)
        if not is_superuser and (
            url.created_by is None or url.created_by != actor_id
        ):
            raise ApiError(403, "You do not have permission to delete this URL")
        await self.delete(url_id)
        await remove_url(self.db, url_id)
        await AuditService(self.db).record_domain(
            action="url.deleted",
            resource_type="url",
            resource_id=url_id,
            actor_id=actor_id,
        )
