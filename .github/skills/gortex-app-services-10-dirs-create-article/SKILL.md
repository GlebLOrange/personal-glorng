---
name: gortex-app-services-10-dirs-create-article
description: "Work in the app/services +10 dirs · create_article area — 116 symbols across 19 files (71% cohesion)"
---

# app/services +10 dirs · create_article

116 symbols | 19 files | 71% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `server/app/core/deps.py`
- `server/app/core/exceptions.py`
- `server/app/db/documents/news.py`
- `server/app/db/repositories/news.py`
- `server/app/db/seed/builders/demo.py`
- `server/app/routers/tools/news.py`
- `server/app/schemas/news.py`
- `server/app/services/calendar.py`
- `server/app/services/maintenance.py`
- `server/app/services/news.py`
- `server/app/services/search_indexers/__init__.py`
- `server/app/services/search_indexers/news.py`
- `server/app/services/user.py`
- `server/app/workers/tasks.py`
- `server/tests/test_news.py`
- `server/tests/test_news_stats.py`
- `server/tests/test_schemas_validators.py`
- `server/tests/test_seo.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | update |
| `server/app/core/deps.py` | audit_svc, get_news_service, registry |
| `server/app/core/exceptions.py` | ConflictError, __init__, message |
| `server/app/db/documents/news.py` | NewsArticle |
| `server/app/db/repositories/news.py` | get_by_slug, slug |
| `server/app/db/seed/builders/demo.py` | count, sources, build_demo_news_articles |
| `server/app/routers/tools/news.py` | user, user, svc, create_news_article, data, ... |
| `server/app/schemas/news.py` | NewsArticleCreate, NewsArticleResponse, NewsArticleListResponse, NewsArticleUpdate |
| `server/app/services/calendar.py` | task, _update_event_sync, event_id, cred, reminder_minutes |
| `server/app/services/maintenance.py` | _assert_not_running |
| `server/app/services/news.py` | article_id, source, _apply_article_updates, list_tags, audit_svc, ... |
| `server/app/services/search_indexers/__init__.py` | registry, _reindex_news |
| `server/app/services/search_indexers/news.py` | registry, index_news_article, article |
| `server/app/services/user.py` | ensure_user_mutable, user |
| `server/app/workers/tasks.py` | article_id, _publish, publish_news_telegram |
| `server/tests/test_news.py` | registry, status, title, _article, test_create_article_persists_required_fields, ... |
| `server/tests/test_news_stats.py` | slug, status, _article |
| `server/tests/test_schemas_validators.py` | test_news_article_create_sanitizes_shared_text_fields |
| `server/tests/test_seo.py` | slug, _published_article |

## Entry Points

- `server/app/services/news.py::NewsService.update_article`

## Connected Communities

- **app/services +11 dirs · delete** (9 cross-edges)
- **tests +17 dirs** (7 cross-edges)
- **app/services +7 dirs · _get_or_create_source_for_url** (3 cross-edges)
- **app/services +15 dirs** (3 cross-edges)
- **app/services +12 dirs** (3 cross-edges)
- **app/services +11 dirs · ApiError** (2 cross-edges)
- **. +8 dirs · app.core.logging.logger** (2 cross-edges)
- **seed/core +7 dirs** (2 cross-edges)
- **app/schemas +8 dirs** (1 cross-edges)
- **tests +10 dirs** (1 cross-edges)
- **. +12 dirs** (1 cross-edges)
- **app/services · remove_by_source** (1 cross-edges)
- **app/services +7 dirs · upsert** (1 cross-edges)
- **app/services +8 dirs · escape** (1 cross-edges)
- **. +2 dirs · escape** (1 cross-edges)
- **. +3 dirs · list_expenses** (1 cross-edges)
- **. +1 dirs · _build_service** (1 cross-edges)
- **app/services +7 dirs · lower** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-450")
explore(operation:"context", task:"understand app/services +10 dirs · create_article", format:"gcx")
relations(operation:"usages", target:{symbol:"server/app/services/news.py::NewsService.update_article"}, format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
