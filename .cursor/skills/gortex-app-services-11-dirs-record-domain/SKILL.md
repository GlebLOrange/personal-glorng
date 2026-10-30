---
name: gortex-app-services-11-dirs-record-domain
description: "Work in the app/services +11 dirs · record_domain area — 390 symbols across 58 files (71% cohesion)"
---

# app/services +11 dirs · record_domain

390 symbols | 58 files | 71% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `external-call::dep:fastapi.Path`
- `external-call::stdlib:segno`
- `server/app/core/deps.py`
- `server/app/core/exceptions.py`
- `server/app/core/permissions.py`
- `server/app/core/redis.py`
- `server/app/core/uploads.py`
- `server/app/core/user_cache.py`
- `server/app/core/utils.py`
- `server/app/db/documents/app_log.py`
- `server/app/db/documents/base.py`
- `server/app/db/documents/credential.py`
- `server/app/db/documents/fileshare.py`
- `server/app/db/documents/health_checker.py`
- `server/app/db/documents/import_batch.py`
- `server/app/db/documents/qr_code.py`
- `server/app/db/documents/task.py`
- `server/app/db/documents/url.py`
- `server/app/db/repositories/base.py`
- `server/app/db/repositories/data_import.py`
- `server/app/db/repositories/fileshare.py`
- `server/app/db/repositories/health_checker.py`
- `server/app/db/repositories/news.py`
- `server/app/db/repositories/user.py`
- `server/app/db/seed/demo/tools/urls.py`
- `server/app/routers/seo.py`
- `server/app/routers/tools/fileshare.py`
- `server/app/routers/tools/news.py`
- `server/app/routers/tools/news_sources.py`
- `server/app/routers/tools/qr_generator.py`
- `server/app/routers/tools/urlshortener.py`
- `server/app/routers/weather.py`
- `server/app/schemas/fileshare.py`
- `server/app/schemas/health_checker.py`
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
- `server/tests/test_health_checker_probe.py`
- `server/tests/test_news_source_delete.py`
- `server/tests/test_tools/test_urlshortener.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | to_thread |
| `external-call::dep:fastapi.Path` | fastapi.Path |
| `external-call::stdlib:segno` | segno |
| `server/app/core/deps.py` | get_audit_service, registry, postgres_db |
| `server/app/core/exceptions.py` | __init__, message, NotFoundError |
| `server/app/core/permissions.py` | key, user_has_permission, user |
| `server/app/core/redis.py` | key, cache_delete |
| `server/app/core/uploads.py` | read_upload_bounded, max_size, file |
| `server/app/core/user_cache.py` | invalidate_user_cache, public_id |
| `server/app/core/utils.py` | generate_short_code, length, chunk_size, path, iter_file |
| `server/app/db/documents/app_log.py` | error, occurred_at, message, error_type, id, ... |
| `server/app/db/documents/base.py` | utc_now, TimestampedDocument |
| `server/app/db/documents/credential.py` | calendar_id, __init__, sync_token, id, created_at, ... |
| `server/app/db/documents/fileshare.py` | SharedFile |
| `server/app/db/documents/health_checker.py` | HealthCheckResult, HealthMonitor |
| `server/app/db/documents/import_batch.py` | ImportBatch |
| `server/app/db/documents/qr_code.py` | QrCode |
| `server/app/db/documents/task.py` | new_status, changed_at, id, old_status, __init__, ... |
| `server/app/db/documents/url.py` | ShortenedUrl |
| `server/app/db/repositories/base.py` | doc_id, get_or_none, delete, doc, doc_id, ... |
| `server/app/db/repositories/data_import.py` | delete_batch, batch_id, batch_id, delete_for_batch |
| `server/app/db/repositories/fileshare.py` | get_by_code, code |
| `server/app/db/repositories/health_checker.py` | user_id, cutoff, delete_older_than, delete_for_monitor, monitor_id, ... |
| `server/app/db/repositories/news.py` | clear_source_id, source_id |
| `server/app/db/repositories/user.py` | doc_id, delete, doc_id, update_fields, fields |
| `server/app/db/seed/demo/tools/urls.py` | count, seed_demo_short_urls, owners, registry |
| `server/app/routers/seo.py` | slug, registry, news_og_html |
| `server/app/routers/tools/fileshare.py` | registry, user, file, upload_file, user, ... |
| `server/app/routers/tools/news.py` | delete_news_article, user, article_id, svc |
| `server/app/routers/tools/news_sources.py` | delete_source, source_id, svc, user |
| `server/app/routers/tools/qr_generator.py` | create_saved_qr_code, data, registry, update_saved_qr_code, user, ... |
| `server/app/routers/tools/urlshortener.py` | user, url_id, redirect_short_url, code, registry, ... |
| `server/app/routers/weather.py` | location, lookup_weather, lookup_world_time, location |
| `server/app/schemas/fileshare.py` | SharedFileResponse |
| `server/app/schemas/health_checker.py` | HealthHistoryPoint, HealthHistoryResponse |
| `server/app/schemas/qr_generator.py` | QrCodeStoredResponse, content_preview, QrCodeUpdate, QrCodeListItem, content |
| `server/app/schemas/url.py` | UrlResponse |
| `server/app/services/account.py` | registry, user, delete_account, current_password |
| `server/app/services/audit.py` | metadata, resource_type, AuditService, actor_type, source, ... |
| `server/app/services/data_import.py` | registry, user_id, repo, _persist_import_rows, error_count, ... |
| `server/app/services/expense.py` | delete_expense, expense_id |
| `server/app/services/fileshare.py` | _resolve_share_path, download_media_type, registry, user_id, contents, ... |
| `server/app/services/health_checker.py` | compute_uptime_percent, delete_monitor, actor_id, monitor_id, fields, ... |
| `server/app/services/news.py` | delete_article, actor_id, actor_id, article_id, delete_source, ... |
| `server/app/services/qr_generator.py` | _assert_can_access, created_by, delete_saved, registry, list_by_owner, ... |
| `server/app/services/recipe.py` | recipe_id, delete_recipe, actor_id |
| `server/app/services/search_indexers/__init__.py` | registry, _reindex_urls |
| `server/app/services/search_indexers/url.py` | registry, index_url, url |
| `server/app/services/task.py` | __init__, audit_svc, registry |
| `server/app/services/url.py` | registry, is_superuser, is_superuser, list_by_owner, get_by_code, ... |
| `server/app/services/weather.py` | WeatherService |
| `server/tests/factories.py` | create_short_url, created_by, title, original_url, registry |
| `server/tests/test_file_share.py` | monkeypatch, test_cleanup_expired_removes_row_and_disk_file, test_download_expired_file, client, registry, ... |
| `server/tests/test_fileshare_datetime.py` | registry, test_get_by_code_expired_naive_datetime |
| `server/tests/test_fileshare_path.py` | tmp_path, monkeypatch, test_get_by_code_rejects_escaped_file_path, monkeypatch, registry, ... |
| `server/tests/test_health_checker_probe.py` | test_compute_uptime_percent_partial, test_compute_uptime_percent_empty, test_compute_uptime_percent_all_ok |
| `server/tests/test_news_source_delete.py` | test_delete_source_detaches_articles, registry |
| `server/tests/test_tools/test_urlshortener.py` | auth_client, test_delete_url, registry, client, auth_client, ... |

## Connected Communities

- **db/repositories +17 dirs** (32 cross-edges)
- **app/services +11 dirs · ApiError** (15 cross-edges)
- **app/services +10 dirs** (11 cross-edges)
- **tests +6 dirs · create_user** (7 cross-edges)
- **. +8 dirs · app.core.logging.logger** (7 cross-edges)
- **app/services +15 dirs** (6 cross-edges)
- **routers/tools +10 dirs** (5 cross-edges)
- **app/services +8 dirs · record** (5 cross-edges)
- **tests +10 dirs** (5 cross-edges)
- **app/services · remove_by_source** (4 cross-edges)
- **tests +5 dirs** (4 cross-edges)
- **app/schemas +8 dirs** (4 cross-edges)
- **app/services +7 dirs · _get_or_create_source_for_url** (3 cross-edges)
- **app/core +7 dirs** (2 cross-edges)
- **services/search_indexers +6 dirs** (2 cross-edges)
- **app/services +7 dirs · lower** (2 cross-edges)
- **app · list_recipes** (2 cross-edges)
- **tests +7 dirs** (2 cross-edges)
- **tests +3 dirs** (2 cross-edges)
- **. +2 dirs · github_authorize** (1 cross-edges)
- **. +3 dirs · list_expenses** (1 cross-edges)
- **app/services +8 dirs · escape** (1 cross-edges)
- **app/services +4 dirs** (1 cross-edges)
- **seed/core +7 dirs** (1 cross-edges)
- **app · get_import_batch** (1 cross-edges)
- **. +4 dirs · download_video** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-446")
explore(operation:"context", task:"understand app/services +11 dirs · record_domain", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
