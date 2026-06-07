from dataclasses import dataclass

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.core.logging import logger
from app.db.models.search_document import SearchDocument, SearchVisibility
from app.db.search_index import SEARCH_INDEX_CONFIG

SNIPPET_MAX_LEN = 600
DEFAULT_SEARCH_LIMIT = 6


@dataclass(frozen=True)
class SearchDocumentInput:
    source_type: str
    source_id: int
    title: str
    body: str
    url: str
    visibility: SearchVisibility


@dataclass(frozen=True)
class SearchResult:
    id: int
    title: str
    body: str
    url: str
    source_type: str
    visibility: str
    source_id: int


def _search_vector() -> ColumnElement:
    return func.to_tsvector(
        SEARCH_INDEX_CONFIG,
        func.concat(SearchDocument.title, " ", SearchDocument.body),
    )


def _truncate_snippet(text: str, *, max_len: int = SNIPPET_MAX_LEN) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_len:
        return cleaned
    return f"{cleaned[: max_len - 3].rstrip()}..."


def _escape_like_pattern(query: str) -> str:
    escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _row_to_result(row: SearchDocument) -> SearchResult:
    return SearchResult(
        id=row.id,
        title=row.title,
        body=row.body,
        url=row.url,
        source_type=row.source_type,
        visibility=row.visibility,
        source_id=row.source_id,
    )


class SearchIndexService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def upsert(self, document: SearchDocumentInput) -> SearchDocument:
        result = await self.db.execute(
            select(SearchDocument).where(
                SearchDocument.source_type == document.source_type,
                SearchDocument.source_id == document.source_id,
            ),
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = SearchDocument(
                source_type=document.source_type,
                source_id=document.source_id,
                title=document.title,
                body=document.body,
                url=document.url,
                visibility=document.visibility,
            )
            self.db.add(row)
        else:
            row.title = document.title
            row.body = document.body
            row.url = document.url
            row.visibility = document.visibility

        await self.db.flush()
        await self.db.refresh(row)
        logger.info(
            "Search document indexed",
            context={
                "source_type": document.source_type,
                "source_id": document.source_id,
            },
        )
        return row

    async def delete_by_source(self, source_type: str, source_id: int) -> None:
        await self.db.execute(
            delete(SearchDocument).where(
                SearchDocument.source_type == source_type,
                SearchDocument.source_id == source_id,
            ),
        )
        await self.db.flush()

    async def delete_stale_by_source(
        self,
        source_type: str,
        keep_source_ids: set[int],
    ) -> None:
        stmt = delete(SearchDocument).where(SearchDocument.source_type == source_type)
        if keep_source_ids:
            stmt = stmt.where(SearchDocument.source_id.not_in(keep_source_ids))
        await self.db.execute(stmt)
        await self.db.flush()

    async def search(
        self,
        query: str,
        *,
        visibilities: list[SearchVisibility],
        limit: int = DEFAULT_SEARCH_LIMIT,
        source_types: list[str] | None = None,
    ) -> list[SearchResult]:
        cleaned = query.strip()
        if not cleaned or not visibilities:
            return []

        visibility_values = [v.value for v in visibilities]
        dialect_name = self.db.get_bind().dialect.name

        if dialect_name == "postgresql":
            return await self._search_postgres(
                cleaned,
                visibility_values=visibility_values,
                limit=limit,
                source_types=source_types,
            )
        return await self._search_sqlite(
            cleaned,
            visibility_values=visibility_values,
            limit=limit,
            source_types=source_types,
        )

    def _source_type_filter(
        self,
        source_types: list[str] | None,
    ) -> ColumnElement[bool] | None:
        if not source_types:
            return None
        return SearchDocument.source_type.in_(source_types)

    async def _search_postgres(
        self,
        query: str,
        *,
        visibility_values: list[str],
        limit: int,
        source_types: list[str] | None,
    ) -> list[SearchResult]:
        ts_query = func.plainto_tsquery(SEARCH_INDEX_CONFIG, query)
        rank = func.ts_rank(_search_vector(), ts_query)
        filters: list[ColumnElement[bool]] = [
            SearchDocument.visibility.in_(visibility_values),
            _search_vector().bool_op("@@")(ts_query),
        ]
        source_filter = self._source_type_filter(source_types)
        if source_filter is not None:
            filters.append(source_filter)

        stmt = (
            select(SearchDocument, rank.label("rank"))
            .where(*filters)
            .order_by(rank.desc(), SearchDocument.updated_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return [_row_to_result(row) for row, _rank in result.all()]

    async def _search_sqlite(
        self,
        query: str,
        *,
        visibility_values: list[str],
        limit: int,
        source_types: list[str] | None,
    ) -> list[SearchResult]:
        pattern = _escape_like_pattern(query)
        filters: list[ColumnElement[bool]] = [
            SearchDocument.visibility.in_(visibility_values),
            or_(
                SearchDocument.title.ilike(pattern),
                SearchDocument.body.ilike(pattern),
            ),
        ]
        source_filter = self._source_type_filter(source_types)
        if source_filter is not None:
            filters.append(source_filter)

        stmt = (
            select(SearchDocument)
            .where(*filters)
            .order_by(SearchDocument.updated_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return [_row_to_result(row) for row in result.scalars().all()]

    @staticmethod
    def snippet(text: str) -> str:
        return _truncate_snippet(text)

    @staticmethod
    def to_sources(results: list[SearchResult]) -> list[dict[str, object]]:
        return [
            {
                "id": index,
                "title": hit.title,
                "url": hit.url,
                "source_type": hit.source_type,
                "snippet": _truncate_snippet(hit.body),
            }
            for index, hit in enumerate(results, start=1)
        ]

    @staticmethod
    def build_context_block(results: list[SearchResult]) -> str:
        if not results:
            return "(no matching documents found)"

        blocks: list[str] = []
        for index, hit in enumerate(results, start=1):
            body = _truncate_snippet(hit.body)
            blocks.append(
                f"[{index}] Title: {hit.title}\n"
                f"Source: {hit.source_type}\n"
                f"URL: {hit.url}\n"
                f"Content: {body}",
            )
        return "\n\n".join(blocks)


async def upsert_document(db: AsyncSession, document: SearchDocumentInput) -> None:
    await SearchIndexService(db).upsert(document)


async def remove_by_source(db: AsyncSession, source_type: str, source_id: int) -> None:
    await SearchIndexService(db).delete_by_source(source_type, source_id)
