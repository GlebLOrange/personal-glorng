from app.services.elasticsearch_search import _search_query, document_id


def test_document_id_is_stable() -> None:
    assert document_id("recipe", 42) == "recipe:42"


def test_search_query_includes_visibility_filter() -> None:
    query = _search_query(
        "vue",
        visibility_values=["public"],
        source_types=None,
    )
    filters = query["bool"]["filter"]
    assert {"terms": {"visibility": ["public"]}} in filters
    assert "must_not" not in query["bool"]


def test_search_query_includes_source_type_filter() -> None:
    query = _search_query(
        "vue",
        visibility_values=["public", "admin"],
        source_types=["recipe", "task"],
    )
    filters = query["bool"]["filter"]
    assert {"terms": {"source_type": ["recipe", "task"]}} in filters
