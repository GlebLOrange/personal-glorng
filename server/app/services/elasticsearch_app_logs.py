"""Elasticsearch index for persisted application logs."""

from datetime import date, datetime
from typing import Any

from elasticsearch import AsyncElasticsearch

from app.core.elasticsearch import get_elasticsearch_client, is_elasticsearch_enabled
from app.core.logging import logger
from app.db.documents.app_log import AppLog
from app.settings import get_settings

APP_LOGS_INDEX_MAPPINGS: dict[str, Any] = {
    "properties": {
        "id": {"type": "integer"},
        "occurred_at": {"type": "date"},
        "level": {"type": "keyword"},
        "logger": {"type": "keyword"},
        "message": {"type": "text"},
        "request_id": {"type": "keyword"},
        "error": {"type": "text"},
        "error_type": {"type": "keyword"},
        "traceback": {"type": "text"},
    },
}


def _index_name() -> str:
    return get_settings().ELASTICSEARCH_APP_LOGS_INDEX


def _app_log_enabled() -> bool:
    return get_settings().app_log_es_enabled() and is_elasticsearch_enabled()


def _document_body(log: AppLog) -> dict[str, Any]:
    occurred_at = log.occurred_at
    if isinstance(occurred_at, datetime):
        occurred_at_value = occurred_at.isoformat()
    else:
        occurred_at_value = datetime.now().isoformat()

    return {
        "id": log.id,
        "occurred_at": occurred_at_value,
        "level": log.level,
        "logger": log.logger,
        "message": log.message,
        "request_id": log.request_id,
        "error": log.error,
        "error_type": log.error_type,
        "traceback": log.traceback,
    }


def _hit_to_app_log(source: dict[str, Any]) -> AppLog:
    occurred_raw = source.get("occurred_at")
    occurred_at = None
    if isinstance(occurred_raw, str):
        occurred_at = datetime.fromisoformat(occurred_raw.replace("Z", "+00:00"))
    return AppLog(
        id=int(source["id"]),
        occurred_at=occurred_at,
        level=str(source.get("level", "info")),
        message=str(source.get("message", "")),
        logger=str(source.get("logger", "glorng")),
        context=None,
        error=source.get("error"),
        error_type=source.get("error_type"),
        traceback=source.get("traceback"),
        request_id=source.get("request_id"),
    )


async def ensure_app_logs_index(client: AsyncElasticsearch | None = None) -> None:
    if not _app_log_enabled():
        return

    es = client or get_elasticsearch_client()
    index = _index_name()
    exists = await es.indices.exists(index=index)
    if exists:
        return

    await es.indices.create(index=index, mappings=APP_LOGS_INDEX_MAPPINGS)
    logger.info("Elasticsearch app logs index created", context={"index": index})


async def index_app_logs(logs: list[AppLog]) -> None:
    if not _app_log_enabled() or not logs:
        return

    es = get_elasticsearch_client()
    await ensure_app_logs_index(es)
    index = _index_name()
    operations: list[dict[str, Any]] = []
    for log in logs:
        if not log.id:
            continue
        operations.append({"index": {"_index": index, "_id": str(log.id)}})
        operations.append(_document_body(log))

    if not operations:
        return

    await es.bulk(operations=operations, refresh=False)


def _search_query(
    message: str,
    *,
    level: str | None,
    request_id: str | None,
    date_from: date | None,
    date_to: date | None,
) -> dict[str, Any]:
    filters: list[dict[str, Any]] = []
    if level:
        filters.append({"term": {"level": level.lower()}})
    if request_id:
        filters.append({"term": {"request_id": request_id.strip()}})
    if date_from or date_to:
        occurred: dict[str, str] = {}
        if date_from:
            occurred["gte"] = datetime.combine(date_from, datetime.min.time()).isoformat()
        if date_to:
            occurred["lte"] = datetime.combine(date_to, datetime.max.time()).isoformat()
        filters.append({"range": {"occurred_at": occurred}})

    return {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": message,
                        "fields": ["message", "traceback", "error"],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                    },
                },
            ],
            "filter": filters,
        },
    }


async def search_app_logs(
    *,
    message: str,
    level: str | None = None,
    request_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[AppLog], int] | None:
    if not _app_log_enabled():
        return None

    cleaned = message.strip()
    if not cleaned:
        return None

    es = get_elasticsearch_client()
    query = _search_query(
        cleaned,
        level=level,
        request_id=request_id,
        date_from=date_from,
        date_to=date_to,
    )
    response = await es.search(
        index=_index_name(),
        query=query,
        from_=offset,
        size=limit,
        sort=[{"occurred_at": "desc"}],
        track_total_hits=True,
    )
    total = int(response["hits"]["total"]["value"])
    items = [_hit_to_app_log(hit["_source"]) for hit in response["hits"]["hits"]]
    return items, total
