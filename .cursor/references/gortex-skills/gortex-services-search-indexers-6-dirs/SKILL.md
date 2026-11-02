---
name: gortex-services-search-indexers-6-dirs
description: "Work in the services/search_indexers +6 dirs area — 105 symbols across 18 files (70% cohesion)"
---

# services/search_indexers +6 dirs

105 symbols | 18 files | 70% cohesion

## When to Use

Use this skill when working on files in:
- `external-call::dep:app.services.search_index.SearchDocumentInput`
- `server/app/core/deps.py`
- `server/app/db/documents/search.py`
- `server/app/db/repositories/search.py`
- `server/app/services/elasticsearch_search.py`
- `server/app/services/recipe.py`
- `server/app/services/search_index.py`
- `server/app/services/search_indexers/__init__.py`
- `server/app/services/search_indexers/expense.py`
- `server/app/services/search_indexers/feedback.py`
- `server/app/services/search_indexers/github.py`
- `server/app/services/search_indexers/resume.py`
- `server/app/services/search_indexers/url.py`
- `server/app/services/search_types.py`
- `server/tests/test_admin_search_api.py`
- `server/tests/test_elasticsearch_search.py`
- `server/tests/test_postgres_integration.py`
- `server/tests/test_search_index.py`

## Key Files

| File | Symbols |
|------|---------|
| `external-call::dep:app.services.search_index.SearchDocumentInput` | app.services.search_index.SearchDocumentInput |
| `server/app/core/deps.py` | get_search_index_service, registry, postgres_db |
| `server/app/db/documents/search.py` | SearchDocument, SearchVisibility |
| `server/app/db/repositories/search.py` | keep_source_ids, get_by_source, document, source_type, source_type, ... |
| `server/app/services/elasticsearch_search.py` | query, limit, visibility_values, rows, source_types, ... |
| `server/app/services/recipe.py` | registry, __init__, audit_svc, search_svc |
| `server/app/services/search_index.py` | __init__, _search_mongo, _row_to_result, keep_source_ids, _upsert_postgres, ... |
| `server/app/services/search_indexers/__init__.py` | _reindex_feedback, registry |
| `server/app/services/search_indexers/expense.py` | expense, _expense_document |
| `server/app/services/search_indexers/feedback.py` | feedback, index_feedback, feedback, registry, _feedback_document |
| `server/app/services/search_indexers/github.py` | repos, _username, registry, index_github_repos |
| `server/app/services/search_indexers/resume.py` | index_resume, registry |
| `server/app/services/search_indexers/url.py` | _url_document, url |
| `server/app/services/search_types.py` | SearchResult, SearchDocumentInput |
| `server/tests/test_admin_search_api.py` | auth_client, test_admin_search_returns_admin_hits, registry, test_admin_search_filters_by_source_type, registry, ... |
| `server/tests/test_elasticsearch_search.py` | test_search_query_includes_source_type_filter, test_search_query_includes_visibility_filter |
| `server/tests/test_postgres_integration.py` | registry, test_search_upsert_and_query_postgres, monkeypatch, postgres_session |
| `server/tests/test_search_index.py` | test_search_index_visibility_filter, document, monkeypatch, registry, fail_upsert_postgres, ... |

## Connected Communities

- **app/services +15 dirs** (9 cross-edges)
- **app/services +5 dirs** (9 cross-edges)
- **db/repositories +17 dirs** (7 cross-edges)
- **. +8 dirs · app.core.logging.logger** (6 cross-edges)
- **tests +10 dirs** (5 cross-edges)
- **tests +5 dirs** (4 cross-edges)
- **. +2 dirs · _search_postgres_fts** (3 cross-edges)
- **. +12 dirs** (1 cross-edges)
- **app/services +7 dirs · lower** (1 cross-edges)
- **app/core +5 dirs** (1 cross-edges)
- **app/services +11 dirs · record_domain** (1 cross-edges)
- **app · promote_batch** (1 cross-edges)
- **db/repositories +12 dirs** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-463")
explore(operation:"context", task:"understand services/search_indexers +6 dirs", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
