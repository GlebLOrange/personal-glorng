from datetime import datetime
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError

from app.core.elasticsearch import get_elasticsearch_client, is_elasticsearch_enabled
from app.core.logging import logger
from app.db.models.search_document import SearchDocument, SearchVisibility
from app.services.search_types import SearchResult
from app.settings import get_settings

INDEX_MAPPINGS: dict[str, Any] = {
    "properties": {
        "pg_id": {"type": "integer"},
        "source_type": {"type": "keyword"},
        "source_id": {"type": "integer"},
        "title": {"type": "text"},
        "body": {"type": "text"},
        "url": {"type": "keyword"},
        "visibility": {"type": "keyword"},
        "updated_at": {"type": "date"},
    },
}


def document_id(source_type: str, source_id: int) -> str:
    return f"{source_type}:{source_id}"


def _index_name() -> str:
    return get_settings().ELASTICSEARCH_INDEX


def _document_body(row: SearchDocument) -> dict[str, Any]:
    updated_at = row.updated_at
    if isinstance(updated_at, datetime):
        updated_at_value = updated_at.isoformat()
    else:
        updated_at_value = datetime.now().isoformat()

    return {
        "pg_id": row.id,
        "source_type": row.source_type,
        "source_id": row.source_id,
        "title": row.title,
        "body": row.body,
        "url": row.url,
        "visibility": row.visibility,
        "updated_at": updated_at_value,
    }


def _hit_to_result(hit: dict[str, Any]) -> SearchResult:
    source = hit["_source"]
    return SearchResult(
        id=int(source["pg_id"]),
        title=str(source["title"]),
        body=str(source["body"]),
        url=str(source["url"]),
        source_type=str(source["source_type"]),
        visibility=str(source["visibility"]),
        source_id=int(source["source_id"]),
    )


async def ensure_index(client: AsyncElasticsearch | None = None) -> None:
    if not is_elasticsearch_enabled():
        return

    es = client or get_elasticsearch_client()
    index = _index_name()
    exists = await es.indices.exists(index=index)
    if exists:
        return

    await es.indices.create(index=index, mappings=INDEX_MAPPINGS)
    logger.info("Elasticsearch index created", context={"index": index})


async def index_document(row: SearchDocument) -> None:
    if not is_elasticsearch_enabled():
        return

    es = get_elasticsearch_client()
    await ensure_index(es)
    doc_id = document_id(row.source_type, row.source_id)
    await es.index(index=_index_name(), id=doc_id, document=_document_body(row))
    logger.info(
        "Elasticsearch document indexed",
        context={"source_type": row.source_type, "source_id": row.source_id},
    )


async def delete_document(source_type: str, source_id: int) -> None:
    if not is_elasticsearch_enabled():
        return

    es = get_elasticsearch_client()
    doc_id = document_id(source_type, source_id)
    try:
        await es.delete(index=_index_name(), id=doc_id)
    except NotFoundError:
        return
    logger.info(
        "Elasticsearch document deleted",
        context={"source_type": source_type, "source_id": source_id},
    )


async def delete_stale_by_source(
    source_type: str,
    keep_source_ids: set[int],
) -> None:
    if not is_elasticsearch_enabled():
        return

    es = get_elasticsearch_client()
    must_not: list[dict[str, Any]] = []
    if keep_source_ids:
        must_not.append({"terms": {"source_id": sorted(keep_source_ids)}})

    query: dict[str, Any] = {
        "bool": {
            "filter": [{"term": {"source_type": source_type}}],
        },
    }
    if must_not:
        query["bool"]["must_not"] = must_not

    await es.delete_by_query(index=_index_name(), query=query, refresh=True)


def _search_query(
    query: str,
    *,
    visibility_values: list[str],
    source_types: list[str] | None,
) -> dict[str, Any]:
    filters: list[dict[str, Any]] = [
        {"terms": {"visibility": visibility_values}},
    ]
    if source_types:
        filters.append({"terms": {"source_type": source_types}})

    return {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^2", "body"],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                    },
                },
            ],
            "filter": filters,
        },
    }


async def search(
    query: str,
    *,
    visibilities: list[SearchVisibility],
    limit: int,
    source_types: list[str] | None = None,
) -> list[SearchResult]:
    if not is_elasticsearch_enabled():
        return []

    es = get_elasticsearch_client()
    visibility_values = [visibility.value for visibility in visibilities]
    response = await es.search(
        index=_index_name(),
        query=_search_query(
            query,
            visibility_values=visibility_values,
            source_types=source_types,
        ),
        size=limit,
        sort=["_score", {"updated_at": "desc"}],
    )
    return [_hit_to_result(hit) for hit in response["hits"]["hits"]]


async def bulk_index_documents(rows: list[SearchDocument]) -> int:
    if not is_elasticsearch_enabled() or not rows:
        return 0

    es = get_elasticsearch_client()
    await ensure_index(es)
    index = _index_name()
    operations: list[dict[str, Any]] = []
    for row in rows:
        doc_key = document_id(row.source_type, row.source_id)
        operations.append({"index": {"_index": index, "_id": doc_key}})
        operations.append(_document_body(row))

    await es.bulk(operations=operations, refresh=True)
    logger.info("Elasticsearch bulk index complete", context={"documents": len(rows)})
    return len(rows)
