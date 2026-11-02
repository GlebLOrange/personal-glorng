---
name: gortex-app-services-11-dirs-delete
description: "Work in the app/services +11 dirs · delete area — 339 symbols across 52 files (70% cohesion)"
---

# app/services +11 dirs · delete

339 symbols | 52 files | 70% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `external-call::dep:fastapi.Path`
- `external-call::stdlib:segno`
- `server/app/core/deps.py`
- `server/app/core/exceptions.py`
- `server/app/core/permissions.py`
- `server/app/core/uploads.py`
- `server/app/core/utils.py`
- `server/app/db/documents/fileshare.py`
- `server/app/db/documents/import_batch.py`
- `server/app/db/documents/qr_code.py`
- `server/app/db/documents/url.py`
- `server/app/db/repositories/base.py`
- `server/app/db/repositories/data_import.py`
- `server/app/db/repositories/fileshare.py`
- `server/app/db/repositories/health_checker.py`
- `server/app/db/repositories/news.py`
- `server/app/db/seed/demo/tools/urls.py`
- `server/app/routers/seo.py`
- `server/app/routers/tools/data_extract.py`
- `server/app/routers/tools/fileshare.py`
- `server/app/routers/tools/news.py`
- `server/app/routers/tools/news_sources.py`
- `server/app/routers/tools/qr_generator.py`
- `server/app/routers/tools/urlshortener.py`
- `server/app/routers/weather.py`
- `server/app/schemas/data_extract.py`
- `server/app/schemas/fileshare.py`
- `server/app/schemas/news.py`
- `server/app/schemas/qr_generator.py`
- `server/app/schemas/url.py`
- `server/app/services/account.py`
- `server/app/services/audit.py`
- `server/app/services/data_import.py`
- `server/app/services/expense.py`
- `server/app/services/fileshare.py`
- `server/app/services/health_checker.py`
- `server/app/services/news.py`
- `server/app/services/qr_generator.py`
- `server/app/services/recipe.py`
- `server/app/services/search_indexers/__init__.py`
- `server/app/services/search_indexers/url.py`
- `server/app/services/task.py`
- `server/app/services/url.py`
- `server/app/services/weather.py`
- `server/tests/factories.py`
- `server/tests/test_file_share.py`
- `server/tests/test_fileshare_datetime.py`
- `server/tests/test_fileshare_path.py`
- `server/tests/test_news_source_delete.py`
- `server/tests/test_news_stats.py`
- `server/tests/test_tools/test_urlshortener.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | to_thread |
| `external-call::dep:fastapi.Path` | fastapi.Path |
| `external-call::stdlib:segno` | segno |
| `server/app/core/deps.py` | get_audit_service, postgres_db, registry |
| `server/app/core/exceptions.py` | message, __init__, NotFoundError |
| `server/app/core/permissions.py` | user_has_permission, user, key |
| `server/app/core/uploads.py` | max_size, read_upload_bounded, file |
| `server/app/core/utils.py` | generate_short_code, length, path, iter_file, utc_now, ... |
| `server/app/db/documents/fileshare.py` | SharedFile |
| `server/app/db/documents/import_batch.py` | ImportBatch |
| `server/app/db/documents/qr_code.py` | QrCode |
| `server/app/db/documents/url.py` | ShortenedUrl |
| `server/app/db/repositories/base.py` | update_fields, doc_id, fields, delete, doc_id, ... |
| `server/app/db/repositories/data_import.py` | delete_batch, batch_id, delete_for_batch, batch_id |
| `server/app/db/repositories/fileshare.py` | get_by_code, code |
| `server/app/db/repositories/health_checker.py` | delete_for_monitors, monitor_ids, delete_for_created_by, user_id |
| `server/app/db/repositories/news.py` | count_articles_by_status |
| `server/app/db/seed/demo/tools/urls.py` | count, registry, owners, seed_demo_short_urls |
| `server/app/routers/seo.py` | slug, news_og_html, registry |
| `server/app/routers/tools/data_extract.py` | user, get_import_batch, batch_id, registry |
| `server/app/routers/tools/fileshare.py` | code, delete_file, registry, file_id, user, ... |
| `server/app/routers/tools/news.py` | get_news_stats, svc, delete_news_article, article_id, svc, ... |
| `server/app/routers/tools/news_sources.py` | delete_source, svc, source_id, user |
| `server/app/routers/tools/qr_generator.py` | get_saved_qr_svg, user, data, delete_saved_qr_code, registry, ... |
| `server/app/routers/tools/urlshortener.py` | code, user, redirect_short_url, url_id, registry, ... |
| `server/app/routers/weather.py` | location, lookup_weather, location, lookup_world_time |
| `server/app/schemas/data_extract.py` | ImportRowResponse, ImportBatchDetailResponse |
| `server/app/schemas/fileshare.py` | SharedFileResponse |
| `server/app/schemas/news.py` | NewsStatsResponse |
| `server/app/schemas/qr_generator.py` | content, QrCodeUpdate, QrCodeStoredResponse, QrCodeListItem, content_preview |
| `server/app/schemas/url.py` | UrlResponse |
| `server/app/services/account.py` | delete_account, registry, current_password, user |
| `server/app/services/audit.py` | postgres_db, __init__, resource_id, metadata, AuditService, ... |
| `server/app/services/data_import.py` | import_rows, preview_limit, user, _persist_import_rows, assert_batch_access, ... |
| `server/app/services/expense.py` | expense_id, delete_expense |
| `server/app/services/fileshare.py` | upload, _resolve_share_path, user_id, registry, user_id, ... |
| `server/app/services/health_checker.py` | is_superuser, monitor_id, monitor_id, delete_monitor, is_superuser, ... |
| `server/app/services/news.py` | slug, delete_article, delete_source, actor_id, actor_id, ... |
| `server/app/services/qr_generator.py` | list_by_owner, actor_id, _repo, create_saved, qr_id, ... |
| `server/app/services/recipe.py` | actor_id, delete_recipe, recipe_id |
| `server/app/services/search_indexers/__init__.py` | _reindex_urls, registry |
| `server/app/services/search_indexers/url.py` | url, registry, index_url |
| `server/app/services/task.py` | __init__, audit_svc, registry |
| `server/app/services/url.py` | code, url_id, actor_id, delete_url, update_url, ... |
| `server/app/services/weather.py` | WeatherService |
| `server/tests/factories.py` | original_url, create_short_url, title, registry, created_by |
| `server/tests/test_file_share.py` | registry, auth_client, test_upload_retries_when_share_code_collides, test_download_expired_file, registry, ... |
| `server/tests/test_fileshare_datetime.py` | test_get_by_code_expired_naive_datetime, registry |
| `server/tests/test_fileshare_path.py` | registry, monkeypatch, monkeypatch, tmp_path, test_resolve_share_path_rejects_traversal, ... |
| `server/tests/test_news_source_delete.py` | test_delete_source_detaches_articles, registry |
| `server/tests/test_news_stats.py` | test_news_stats_counts_by_status, registry |
| `server/tests/test_tools/test_urlshortener.py` | auth_client, registry, auth_client, test_delete_url_via_api, admin_user, ... |

## Connected Communities

- **tests +17 dirs** (26 cross-edges)
- **app/services +11 dirs · ApiError** (16 cross-edges)
- **app/services +10 dirs · create_article** (10 cross-edges)
- **tests +6 dirs · create_user** (7 cross-edges)
- **app/services +15 dirs** (6 cross-edges)
- **. +8 dirs · app.core.logging.logger** (6 cross-edges)
- **app/schemas +8 dirs** (5 cross-edges)
- **app/services +8 dirs · record** (5 cross-edges)
- **tests +10 dirs** (5 cross-edges)
- **tests +5 dirs** (4 cross-edges)
- **app/services · remove_by_source** (4 cross-edges)
- **app/services +10 dirs · ValidationError** (4 cross-edges)
- **app/db · utc_now** (3 cross-edges)
- **db/documents +3 dirs** (3 cross-edges)
- **app/services +7 dirs · _get_or_create_source_for_url** (3 cross-edges)
- **seed/core +7 dirs** (2 cross-edges)
- **routers/tools +3 dirs** (2 cross-edges)
- **app · list_recipes** (2 cross-edges)
- **app/services +7 dirs · upsert** (2 cross-edges)
- **tests +3 dirs** (2 cross-edges)
- **app/services +7 dirs · lower** (2 cross-edges)
- **. +3 dirs · list_expenses** (1 cross-edges)
- **app/services +8 dirs · escape** (1 cross-edges)
- **app/core +7 dirs** (1 cross-edges)
- **. +2 dirs · github_authorize** (1 cross-edges)
- **. +4 dirs · download_video** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-444")
explore(operation:"context", task:"understand app/services +11 dirs · delete", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
