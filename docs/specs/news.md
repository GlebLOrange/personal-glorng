# Spec: Curated News

## Objective

Build a public curated news digest that publishes short, readable summaries from trusted RSS/Atom feeds. The feature should help visitors scan worldwide news by theme, while preserving attribution and linking to the original publisher for every item.

## Scope

Version 1 ingests only trusted feed metadata: title, excerpt, source, URL, and publication time. It does not scrape full article pages, bypass paywalls, or republish full articles.

## Source Policy

News sources are configured with an allowlist. Each source has a name, feed URL, language, default themes, enabled flag, and per-run cap. Items without a stable source URL are skipped. Duplicate source URLs are not republished.

## AI Contract

AI receives only feed metadata and must return structured JSON:

- `title`: readable title, 90 characters max.
- `summary`: concise paragraph, 600 characters max.
- `bullets`: 2-5 key points, 180 characters max each.
- `themes`: 1-4 allowed theme names.
- `telegram_text`: optional short Telegram body, 900 characters max.

The backend validates lengths and allowed themes before saving. The frontend renders structured fields directly. Telegram HTML is generated and escaped on the backend.

## API Contract

Public:

- `GET /api/tools/news`
- `GET /api/tools/news/themes`
- `GET /api/tools/news/{slug}`

Admin:

- `POST /api/tools/news/ingest`
- `POST /api/tools/news/{id}/telegram`
- `PUT /api/tools/news/{id}`
- `DELETE /api/tools/news/{id}`

## Telegram Template

Telegram posts use HTML parse mode with escaped dynamic values:

```text
<b>{title}</b>

{summary}

• {bullet_1}
• {bullet_2}
• {bullet_3}

Themes: #{theme_1} #{theme_2}
Source: <a href="{source_url}">{source_name}</a>
Read on site: {site_url}/news/{slug}
```

## Success Criteria

- `/news` lists published items with theme filtering.
- `/news/:slug` shows a readable detail page with source attribution.
- A scheduled job can ingest trusted feeds and skip duplicates.
- Valid AI output auto-publishes to the site.
- Telegram posting is retryable and records the message id when successful.
- Admin users can trigger ingestion, unpublish/delete items, and repost to Telegram.
