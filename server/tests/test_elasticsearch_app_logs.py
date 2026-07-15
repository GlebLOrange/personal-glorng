"""Elasticsearch app log index query builder tests."""

from datetime import date

from app.services.elasticsearch_app_logs import _search_query


def test_app_log_search_query_includes_message_match() -> None:
    query = _search_query(
        "recipe failed",
        level=None,
        request_id=None,
        date_from=None,
        date_to=None,
    )
    must = query["bool"]["must"]
    assert must[0]["multi_match"]["query"] == "recipe failed"
    assert "message" in must[0]["multi_match"]["fields"]


def test_app_log_search_query_includes_structured_filters() -> None:
    query = _search_query(
        "timeout",
        level="error",
        request_id="req-123",
        date_from=date(2026, 1, 1),
        date_to=date(2026, 1, 31),
    )
    filters = query["bool"]["filter"]
    assert {"term": {"level": "error"}} in filters
    assert {"term": {"request_id": "req-123"}} in filters
    assert any("range" in item for item in filters)
