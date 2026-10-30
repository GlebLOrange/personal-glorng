---
name: gortex-app-services-7-dirs-upsert
description: "Work in the app/services +7 dirs · upsert area — 157 symbols across 23 files (75% cohesion)"
---

# app/services +7 dirs · upsert

157 symbols | 23 files | 75% cohesion

## When to Use

Use this skill when working on files in:
- `external-call::dep:app.services.search_index.SearchDocumentInput`
- `external-call::dep:sqlalchemy.delete`
- `server/app/core/deps.py`
- `server/app/core/elasticsearch.py`
- `server/app/db/documents/search.py`
- `server/app/db/repositories/search.py`
- `server/app/routers/tools/app_logs.py`
- `server/app/services/app_log.py`
- `server/app/services/elasticsearch_app_logs.py`
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
| `external-call::dep:sqlalchemy.delete` | sqlalchemy.delete |
| `server/app/core/deps.py` | get_search_index_service, registry, postgres_db |
| `server/app/core/elasticsearch.py` | get_elasticsearch_client, is_elasticsearch_enabled |
| `server/app/db/documents/search.py` | SearchVisibility, SearchDocument |
| `server/app/db/repositories/search.py` | source_id, get_by_source, source_type, document, keep_source_ids, ... |
| `server/app/routers/tools/app_logs.py` | registry, get_app_log_service |
| `server/app/services/app_log.py` | level, list_logs, registry, message, __init__, ... |
| `server/app/services/elasticsearch_app_logs.py` | _document_body, sort, date_from, search_app_logs, level, ... |
| `server/app/services/elasticsearch_search.py` | source_types, _document_body, keep_source_ids, query, rows, ... |
| `server/app/services/recipe.py` | audit_svc, registry, search_svc, __init__ |
| `server/app/services/search_index.py` | _search_repo, source_id, document, postgres_db, source_types, ... |
| `server/app/services/search_indexers/__init__.py` | registry, _reindex_feedback |
| `server/app/services/search_indexers/expense.py` | _expense_document, expense |
| `server/app/services/search_indexers/feedback.py` | feedback, feedback, _feedback_document, registry, index_feedback |
| `server/app/services/search_indexers/github.py` | index_github_repos, repos, _username, registry |
| `server/app/services/search_indexers/resume.py` | registry, index_resume |
| `server/app/services/search_indexers/url.py` | _url_document, url |
| `server/app/services/search_types.py` | SearchDocumentInput, SearchResult |
| `server/tests/test_admin_search_api.py` | registry, test_admin_search_filters_by_source_type, test_admin_search_returns_admin_hits, registry, auth_client, ... |
| `server/tests/test_elasticsearch_search.py` | test_document_id_is_stable, test_search_query_includes_source_type_filter, test_search_query_includes_visibility_filter |
| `server/tests/test_postgres_integration.py` | test_search_upsert_and_query_postgres, postgres_session, registry, monkeypatch |
| `server/tests/test_search_index.py` | registry, test_search_index_upsert_and_search, monkeypatch, registry, document, ... |

## Connected Communities

- **app/services +15 dirs** (14 cross-edges)
- **. +8 dirs · app.core.logging.logger** (13 cross-edges)
- **tests +10 dirs** (9 cross-edges)
- **tests +5 dirs** (6 cross-edges)
- **tests +17 dirs** (6 cross-edges)
- **. +2 dirs · _search_postgres_fts** (3 cross-edges)
- **db/repositories +4 dirs** (3 cross-edges)
- **app/services +11 dirs · delete** (2 cross-edges)
- **app/services +12 dirs** (2 cross-edges)
- **db/repositories +12 dirs** (1 cross-edges)
- **app/core +5 dirs** (1 cross-edges)
- **app · promote_batch** (1 cross-edges)
- **app/services +8 dirs · record** (1 cross-edges)
- **. +12 dirs** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-463")
explore(operation:"context", task:"understand app/services +7 dirs · upsert", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
