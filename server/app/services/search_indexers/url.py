from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.search_document import SearchVisibility
from app.db.models.url import ShortenedUrl
from app.services.search_index import SearchDocumentInput, SearchIndexService

URL_SOURCE_TYPE = "url"


def _url_document(url: ShortenedUrl) -> SearchDocumentInput:
    title = url.title or url.code
    body = f"{url.original_url}\nCode: {url.code}\nClicks: {url.clicks}"
    return SearchDocumentInput(
        source_type=URL_SOURCE_TYPE,
        source_id=url.id,
        title=title,
        body=body,
        url="/admin/tools/url-shortener",
        visibility=SearchVisibility.ADMIN,
    )


async def index_url(db: AsyncSession, url: ShortenedUrl) -> None:
    await SearchIndexService(db).upsert(_url_document(url))


async def remove_url(db: AsyncSession, url_id: int) -> None:
    await SearchIndexService(db).delete_by_source(URL_SOURCE_TYPE, url_id)
