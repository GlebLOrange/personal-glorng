# P3 roadmap (current state)

**Status:** Snapshot after P0–P2. Short shipped list + remaining backlog only.

## Shipped

| Item | Notes |
|------|--------|
| TS ~5.9 + green lint/tests/build | `client/package.json`; CI `VITE_PUBLIC_ORIGIN` |
| Chart entry preload guard | `client/scripts/check-entry-preloads.mjs` |
| Vid-download SSRF / cookies / file-share paths | Server tests; tools gated by `UNTRUSTED_URL_TOOLS_ENABLED` |
| News OG HTML + nginx bot routing | `/og/news/{slug}`, `nginx/social_preview_map.conf` |
| Shared expense catalog | `shared/expense_catalog.json` |
| Home canonical / JSON-LD | `client/src/utils/pageSeo.ts`, `useRouteSeo.ts` |

## Started

| Item | Notes |
|------|--------|
| CSS audit + index budget | [Frontend CSS audit](/guide/frontend-css-audit), `client/scripts/check-css-budget.mjs` |

## Backlog

| Item | Notes |
|------|--------|
| Route-level / admin CSS split | Second Vite CSS entry; see CSS audit |
| Static prerender / SSR for `/`, `/news` | CSR meta limits; `/og/news` covers share bots only |
| Platform catalog off entry | `PLATFORM_SERVICES` still pulled into lazy route chunks |
| Firebase slimming | Already dynamic; optional backend-only Google auth |
| Design / positioning pass | Content/UX, not infra |

## Suggested order

1. Monitor `check-css-budget` and Lighthouse on prod `/`.
2. If LCP regresses: prototype an admin CSS entry (one slice).
3. Evaluate prerender only if search/social still miss content after `/og/*` and JSON-LD.

## Out of scope

- Full SSR framework migration
- Replacing Tailwind with per-page CSS modules
