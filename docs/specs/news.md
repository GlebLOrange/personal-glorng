# Spec: Curated News (current state)

**Status:** Shipped on `main`. This page is a status summary; path-level detail lives in the generated OpenAPI catalog.

- 2026-10-26: Ingest Deutsche Welle English only (`https://rss.dw.com/xml/rss-en-all`); `NEWS_INGEST_ENABLED` stays false in Settings and is set true on worker/beat compose; demo `ai_model=demo` articles are drafted; public list accepts one `tag` plus inclusive `date_from`/`date_to` on `source_published_at`; if Groq is unset, publish feed title and excerpt.

## Objective

Public curated news digest from trusted RSS/Atom feeds: short summaries with attribution and links to the original publisher. Visitors browse by tag; admins manage articles and sources.

## Scope (shipped)

- Ingests feed metadata only (title, excerpt, source, URL, publication time) — no full-article scrape or paywall bypass.
- AI rewrite (when configured) returns structured title/summary/bullets/tags; backend validates lengths and tags before save. Without Groq, feed title and excerpt are published as-is.
- Telegram HTML is generated and escaped on the backend.
- Public `GET /api/tools/news` supports optional `tag`, `date_from`, and `date_to`.

## News sources (`NewsSourceResponse`)

Admin source records expose (see `server/app/schemas/news.py`):

| Field | Notes |
|-------|--------|
| `name` | Display name |
| `feed_url` | RSS/Atom URL |
| `host` | Optional host label |
| `category` | Default `world` |
| `region` | Default `global` |
| `enabled` | Whether ingest includes the source |
| `last_error` | Last fetch/parse error, if any |
| `last_fetched_at` | Last successful/attempted fetch time |

Also returned: `id`, `created_at`, `updated_at`. Ingest config may still use language / default themes / per-run caps via `NEWS_SOURCES_JSON` and worker settings — see [Configuration](/reference/configuration#news-ingest).

## API (summary)

Mounted under `/api/tools/news` (sources under `/api/tools/news/sources`). **Authoritative path list:** [API endpoints (generated)](/generated/api-endpoints) (regenerate with `make docs-generate`).

Public (rate limited):

- `GET /api/tools/news` — published list (optional `tag`, `date_from`, `date_to`)
- `GET /api/tools/news/tags`
- `GET /api/tools/news/{slug}`

Admin articles (`news:read` / `news:write`):

- `GET /api/tools/news?manage=true` (optional `status`)
- `GET /api/tools/news/stats`
- `GET /api/tools/news/by-id/{id}`
- `POST /api/tools/news`
- `POST /api/tools/news/ingest`
- `POST /api/tools/news/metadata`
- `POST /api/tools/news/{id}/telegram`
- `PUT /api/tools/news/{id}`
- `DELETE /api/tools/news/{id}`

Admin sources (`news-sources:*`):

- `GET|POST /api/tools/news/sources`
- `POST /api/tools/news/sources/refresh`
- `PUT|DELETE /api/tools/news/sources/{id}`

## Ops pointers

- Env: `NEWS_INGEST_ENABLED`, `NEWS_SOURCES_JSON`, Telegram channel vars — [Configuration](/reference/configuration#news-ingest)
- Social preview: `/og/news/{slug}` + `nginx/social_preview_map.conf`
- How-tos stay on owner pages (security, deployment); this spec does not duplicate them

## Success criteria (met)

- `/news` and `/news/:slug` render published items with tags and source attribution
- Ingest skips duplicates; Telegram publish is retryable and stores message id
- Admins can ingest, edit status, delete, manage sources, and repost to Telegram
