from app.core.exceptions import ApiError, NotFoundError
from app.core.utils import generate_short_code
from app.db.documents.url import ShortenedUrl
from app.db.registry import DatabaseRegistry
from app.services.audit import AuditService
from app.services.search_indexers.url import index_url, remove_url

_MAX_CODE_RETRIES = 3


class UrlService:
    def __init__(self, registry: DatabaseRegistry) -> None:
        self.registry = registry

    def _urls(self):
        if self.registry.urls is None:
            msg = "URL repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.urls

    async def create_short_url(
        self,
        original_url: str,
        created_by: int | None,
        title: str | None = None,
    ) -> ShortenedUrl:
        for attempt in range(_MAX_CODE_RETRIES):
            code = generate_short_code(8)
            existing = await self._urls().get_by_code(code)
            if existing is not None:
                if attempt == _MAX_CODE_RETRIES - 1:
                    raise ApiError(503, "Failed to generate unique short code")
                continue

            url = ShortenedUrl(
                code=code,
                original_url=original_url,
                title=title,
                created_by=created_by,
            )
            url = await self._urls().insert(url)
            await index_url(self.registry, url)
            await AuditService(self.registry).record_domain(
                action="url.created",
                resource_type="url",
                resource_id=url.id,
                actor_id=created_by,
                metadata={"code": url.code},
            )
            return url
        raise ApiError(503, "Failed to generate unique short code")

    async def get_by_code(self, code: str) -> ShortenedUrl:
        url = await self._urls().get_by_code(code)
        if not url:
            raise NotFoundError(f"URL with code '{code}' not found")
        return url

    async def increment_clicks(self, code: str) -> None:
        url = await self.get_by_code(code)
        url = await self._urls().update_fields(url.id, clicks=url.clicks + 1)
        await index_url(self.registry, url)

    async def list_by_owner(
        self,
        created_by: int,
        offset: int = 0,
        limit: int = 20,
    ) -> list[ShortenedUrl]:
        return await self._urls().list(
            offset=offset,
            limit=limit,
            created_by=created_by,
            sort=[("created_at", -1)],
        )

    async def update_url(
        self,
        url_id: int,
        *,
        title: str | None,
        actor_id: int,
        is_superuser: bool = False,
    ) -> ShortenedUrl:
        url = await self._urls().get(url_id)
        if not is_superuser and (url.created_by is None or url.created_by != actor_id):
            raise ApiError(403, "You do not have permission to update this URL")
        url = await self._urls().update_fields(url_id, title=title)
        await index_url(self.registry, url)
        await AuditService(self.registry).record_domain(
            action="url.updated",
            resource_type="url",
            resource_id=url_id,
            actor_id=actor_id,
            metadata={"code": url.code},
        )
        return url

    async def delete_url(
        self,
        url_id: int,
        actor_id: int,
        *,
        is_superuser: bool = False,
    ) -> None:
        url = await self._urls().get(url_id)
        if not is_superuser and (url.created_by is None or url.created_by != actor_id):
            raise ApiError(403, "You do not have permission to delete this URL")
        await self._urls().delete(url_id)
        await remove_url(self.registry, url_id)
        await AuditService(self.registry).record_domain(
            action="url.deleted",
            resource_type="url",
            resource_id=url_id,
            actor_id=actor_id,
        )
