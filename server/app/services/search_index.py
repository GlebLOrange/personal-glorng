from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.core.elasticsearch import is_elasticsearch_enabled
from app.core.logging import logger
from app.db.documents.search import SearchDocument, SearchVisibility
from app.db.registry import DatabaseRegistry
from app.db.search_index import SEARCH_INDEX_CONFIG
from app.services import elasticsearch_search
from app.services.search_types import SearchDocumentInput, SearchResult
from app.settings import get_settings

SNIPPET_MAX_LEN = 600
DEFAULT_SEARCH_LIMIT = 6


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


def _input_to_document(document: SearchDocumentInput) -> SearchDocument:
    return SearchDocument(
        source_type=document.source_type,
        source_id=document.source_id,
        title=document.title,
        body=document.body,
        url=document.url,
        visibility=document.visibility.value,
    )


class SearchIndexService:
    def __init__(
        self,
        registry: DatabaseRegistry,
        *,
        postgres_db: AsyncSession | None = None,
    ) -> None:
        self.registry = registry
        self.postgres_db = postgres_db

    def _search_repo(self):
        if self.registry.search is None:
            msg = "Search repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.search

    async def upsert(self, document: SearchDocumentInput) -> SearchDocument:
        row = await self._search_repo().upsert(_input_to_document(document))
        logger.info(
            "Search document indexed",
            context={
                "source_type": document.source_type,
                "source_id": document.source_id,
            },
        )

        if self.postgres_db is not None and get_settings().enable_postgres():
            await self._upsert_postgres(document)

        if is_elasticsearch_enabled():
            try:
                await elasticsearch_search.index_document(row)
            except Exception as exc:
                logger.error(
                    "Elasticsearch index sync failed",
                    error=exc,
                    context={
                        "source_type": document.source_type,
                        "source_id": document.source_id,
                    },
                )
        return row

    async def _upsert_postgres(self, document: SearchDocumentInput) -> None:
        from app.db.models.search_document import SearchDocument as PgSearchDocument

        if self.postgres_db is None:
            return

        result = await self.postgres_db.execute(
            select(PgSearchDocument).where(
                PgSearchDocument.source_type == document.source_type,
                PgSearchDocument.source_id == document.source_id,
            ),
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = PgSearchDocument(
                source_type=document.source_type,
                source_id=document.source_id,
                title=document.title,
                body=document.body,
                url=document.url,
                visibility=document.visibility,
            )
            self.postgres_db.add(row)
        else:
            row.title = document.title
            row.body = document.body
            row.url = document.url
            row.visibility = document.visibility
        await self.postgres_db.flush()

    async def delete_by_source(self, source_type: str, source_id: int) -> None:
        await self._search_repo().delete_by_source(
            source_type=source_type,
            source_id=source_id,
        )

        if self.postgres_db is not None and get_settings().enable_postgres():
            from app.db.models.search_document import SearchDocument as PgSearchDocument

            await self.postgres_db.execute(
                delete(PgSearchDocument).where(
                    PgSearchDocument.source_type == source_type,
                    PgSearchDocument.source_id == source_id,
                ),
            )
            await self.postgres_db.flush()

        if is_elasticsearch_enabled():
            try:
                await elasticsearch_search.delete_document(source_type, source_id)
            except Exception as exc:
                logger.error(
                    "Elasticsearch delete sync failed",
                    error=exc,
                    context={"source_type": source_type, "source_id": source_id},
                )

    async def delete_stale_by_source(
        self,
        source_type: str,
        keep_source_ids: set[int],
    ) -> None:
        await self._search_repo().delete_stale_by_source(source_type, keep_source_ids)

        if self.postgres_db is not None and get_settings().enable_postgres():
            from app.db.models.search_document import SearchDocument as PgSearchDocument

            stmt = delete(PgSearchDocument).where(
                PgSearchDocument.source_type == source_type,
            )
            if keep_source_ids:
                stmt = stmt.where(PgSearchDocument.source_id.not_in(keep_source_ids))
            await self.postgres_db.execute(stmt)
            await self.postgres_db.flush()

        if is_elasticsearch_enabled():
            try:
                await elasticsearch_search.delete_stale_by_source(
                    source_type,
                    keep_source_ids,
                )
            except Exception as exc:
                logger.error(
                    "Elasticsearch stale delete sync failed",
                    error=exc,
                    context={"source_type": source_type},
                )

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
        if is_elasticsearch_enabled():
            try:
                return await elasticsearch_search.search(
                    cleaned,
                    visibilities=visibilities,
                    limit=limit,
                    source_types=source_types,
                )
            except Exception as exc:
                logger.warning(
                    "Elasticsearch search failed, falling back to database",
                    error=exc,
                )

        mongo_hits = await self._search_mongo(
            cleaned,
            visibility_values=visibility_values,
            limit=limit,
            source_types=source_types,
        )
        if mongo_hits:
            return mongo_hits

        if self.postgres_db is not None and get_settings().enable_postgres():
            return await self._search_postgres(
                cleaned,
                visibility_values=visibility_values,
                limit=limit,
                source_types=source_types,
            )
        return []

    async def _search_mongo(
        self,
        query: str,
        *,
        visibility_values: list[str],
        limit: int,
        source_types: list[str] | None,
    ) -> list[SearchResult]:
        results: list[SearchResult] = []
        for visibility in visibility_values:
            rows = await self._search_repo().search_text(
                query,
                limit=limit,
                visibility=visibility,
            )
            for row in rows:
                if source_types and row.source_type not in source_types:
                    continue
                results.append(_row_to_result(row))
                if len(results) >= limit:
                    return results
        return results[:limit]

    def _search_vector(self) -> ColumnElement:
        from app.db.models.search_document import SearchDocument as PgSearchDocument

        return func.to_tsvector(
            SEARCH_INDEX_CONFIG,
            func.concat(PgSearchDocument.title, " ", PgSearchDocument.body),
        )

    def _source_type_filter(
        self,
        source_types: list[str] | None,
    ) -> ColumnElement[bool] | None:
        from app.db.models.search_document import SearchDocument as PgSearchDocument

        if not source_types:
            return None
        return PgSearchDocument.source_type.in_(source_types)

    async def _search_postgres(
        self,
        query: str,
        *,
        visibility_values: list[str],
        limit: int,
        source_types: list[str] | None,
    ) -> list[SearchResult]:

        if self.postgres_db is None:
            return []

        dialect_name = self.postgres_db.get_bind().dialect.name
        if dialect_name == "postgresql":
            return await self._search_postgres_fts(
                query,
                visibility_values=visibility_values,
                limit=limit,
                source_types=source_types,
            )
        return await self._search_postgres_like(
            query,
            visibility_values=visibility_values,
            limit=limit,
            source_types=source_types,
        )

    async def _search_postgres_fts(
        self,
        query: str,
        *,
        visibility_values: list[str],
        limit: int,
        source_types: list[str] | None,
    ) -> list[SearchResult]:
        from app.db.models.search_document import SearchDocument as PgSearchDocument

        if self.postgres_db is None:
            return []

        ts_query = func.plainto_tsquery(SEARCH_INDEX_CONFIG, query)
        rank = func.ts_rank(self._search_vector(), ts_query)
        filters: list[ColumnElement[bool]] = [
            PgSearchDocument.visibility.in_(visibility_values),
            self._search_vector().bool_op("@@")(ts_query),
        ]
        source_filter = self._source_type_filter(source_types)
        if source_filter is not None:
            filters.append(source_filter)

        stmt = (
            select(PgSearchDocument, rank.label("rank"))
            .where(*filters)
            .order_by(rank.desc(), PgSearchDocument.updated_at.desc())
            .limit(limit)
        )
        result = await self.postgres_db.execute(stmt)
        return [
            SearchResult(
                id=row.id,
                title=row.title,
                body=row.body,
                url=row.url,
                source_type=row.source_type,
                visibility=row.visibility,
                source_id=row.source_id,
            )
            for row, _rank in result.all()
        ]

    async def _search_postgres_like(
        self,
        query: str,
        *,
        visibility_values: list[str],
        limit: int,
        source_types: list[str] | None,
    ) -> list[SearchResult]:
        from app.db.models.search_document import SearchDocument as PgSearchDocument

        if self.postgres_db is None:
            return []

        pattern = _escape_like_pattern(query)
        filters: list[ColumnElement[bool]] = [
            PgSearchDocument.visibility.in_(visibility_values),
            or_(
                PgSearchDocument.title.ilike(pattern),
                PgSearchDocument.body.ilike(pattern),
            ),
        ]
        source_filter = self._source_type_filter(source_types)
        if source_filter is not None:
            filters.append(source_filter)

        stmt = (
            select(PgSearchDocument)
            .where(*filters)
            .order_by(PgSearchDocument.updated_at.desc())
            .limit(limit)
        )
        result = await self.postgres_db.execute(stmt)
        return [
            SearchResult(
                id=row.id,
                title=row.title,
                body=row.body,
                url=row.url,
                source_type=row.source_type,
                visibility=row.visibility,
                source_id=row.source_id,
            )
            for row in result.scalars().all()
        ]

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


async def upsert_document(
    registry: DatabaseRegistry,
    document: SearchDocumentInput,
) -> None:
    await SearchIndexService(registry).upsert(document)


async def remove_by_source(
    registry: DatabaseRegistry,
    source_type: str,
    source_id: int,
) -> None:
    await SearchIndexService(registry).delete_by_source(source_type, source_id)
