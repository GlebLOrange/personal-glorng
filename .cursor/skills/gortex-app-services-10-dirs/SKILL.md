---
name: gortex-app-services-10-dirs
description: "Work in the app/services +10 dirs area — 134 symbols across 20 files (73% cohesion)"
---

# app/services +10 dirs

134 symbols | 20 files | 73% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `server/app/core/deps.py`
- `server/app/core/exceptions.py`
- `server/app/core/utils.py`
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
| `server/app/core/deps.py` | get_news_service, registry, audit_svc |
| `server/app/core/exceptions.py` | ConflictError, __init__, message |
| `server/app/core/utils.py` | utc_now |
| `server/app/db/documents/news.py` | NewsArticle |
| `server/app/db/repositories/news.py` | get_by_slug, slug, count_articles_by_status |
| `server/app/db/seed/builders/demo.py` | sources, count, build_demo_news_articles |
| `server/app/routers/tools/news.py` | update_news_article, article_id, svc, article_id, user, ... |
| `server/app/schemas/news.py` | NewsArticleListResponse, NewsArticleUpdate, NewsStatsResponse, NewsArticleResponse, NewsArticleCreate |
| `server/app/services/calendar.py` | event_id, task, _update_event_sync, cred, reminder_minutes |
| `server/app/services/maintenance.py` | _assert_not_running |
| `server/app/services/news.py` | slug, list_tags, attempted_slug, registry, article_id, ... |
| `server/app/services/search_indexers/__init__.py` | _reindex_news, registry |
| `server/app/services/search_indexers/news.py` | index_news_article, article, registry |
| `server/app/services/user.py` | ensure_user_mutable, user |
| `server/app/workers/tasks.py` | publish_news_telegram, _publish, article_id |
| `server/tests/test_news.py` | registry, title, registry, status, slug, ... |
| `server/tests/test_news_stats.py` | _article, status, registry, test_news_stats_counts_by_status, slug |
| `server/tests/test_schemas_validators.py` | test_news_article_create_sanitizes_shared_text_fields |
| `server/tests/test_seo.py` | _published_article, slug |

## Entry Points

- `server/app/services/news.py::NewsService.update_article`

## Connected Communities

- **db/repositories +17 dirs** (9 cross-edges)
- **app/services +11 dirs · record_domain** (7 cross-edges)
- **seed/core +7 dirs** (3 cross-edges)
- **app/services +7 dirs · _get_or_create_source_for_url** (3 cross-edges)
- **app/services +15 dirs** (3 cross-edges)
- **app/services +12 dirs** (3 cross-edges)
- **app/services +11 dirs · ApiError** (2 cross-edges)
- **. +8 dirs · app.core.logging.logger** (2 cross-edges)
- **. +12 dirs** (1 cross-edges)
- **app/schemas +8 dirs** (1 cross-edges)
- **. +1 dirs · _build_service** (1 cross-edges)
- **. +2 dirs · escape** (1 cross-edges)
- **routers/tools +10 dirs** (1 cross-edges)
- **tests +10 dirs** (1 cross-edges)
- **app/services · remove_by_source** (1 cross-edges)
- **services/search_indexers +6 dirs** (1 cross-edges)
- **app/services +8 dirs · escape** (1 cross-edges)
- **. +3 dirs · list_expenses** (1 cross-edges)
- **app/services +7 dirs · lower** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-451")
explore(operation:"context", task:"understand app/services +10 dirs", format:"gcx")
relations(operation:"usages", target:{symbol:"server/app/services/news.py::NewsService.update_article"}, format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
