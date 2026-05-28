from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApiError, NotFoundError
from app.core.utils import generate_short_code
from app.db.models.url import ShortenedUrl
from app.services.base import CRUDService

_MAX_CODE_RETRIES = 3


class UrlService(CRUDService[ShortenedUrl]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, ShortenedUrl)

    async def create_short_url(
        self,
        original_url: str,
        created_by: int,
        title: str | None = None,
    ) -> ShortenedUrl:
        for attempt in range(_MAX_CODE_RETRIES):
            code = generate_short_code(8)
            try:
                return await self.create(
                    {
                        "code": code,
                        "original_url": original_url,
                        "title": title,
                        "created_by": created_by,
                    }
                )
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
