# P3 roadmap (post P0–P2)

Tracking larger items from the review plan. P0/P1/P2 toolchain, security, SEO, and CSS guardrails are on `main` or PR [#666](https://github.com/GlebLOrange/personal-glorng/pull/666).

## Status key

- **Done** — shipped or verified in repo
- **Started** — partial / guardrails only
- **Backlog** — not started

| Item | Status | Notes |
|------|--------|-------|
| TS ~5.9 + green lint/tests/build | Done | `client/package.json`, CI `VITE_PUBLIC_ORIGIN` |
| Chart entry preload guard | Done | `check-entry-preloads.mjs` |
| Vid-download SSRF, cookies, file-share paths | Done | server tests |
| News OG HTML + nginx bot routing | Done | `/og/news/{slug}`, `social_preview_map.conf` |
| Shared expense catalog (client + server) | Done | `shared/expense_catalog.json` |
| Home canonical / JSON-LD (client) | Done | `pageSeo.ts`, `useRouteSeo.ts` |
| CSS audit + index budget | Started | [Frontend CSS audit](/guide/frontend-css-audit), `check-css-budget.mjs` |
| **Route-level / admin CSS split** | Backlog | Second Vite CSS entry; see CSS audit |
| **Static prerender / SSR** for `/`, `/news` | Backlog | CSR meta limits; `/og/news` mitigates share bots only |
| **Platform catalog off entry** | Backlog | `PLATFORM_SERVICES` still in lazy route chunks (`ToolsPage`); optional slimmer public-only manifest |
| **Firebase slimming** | Backlog | Already dynamic; optional backend-only Google auth |
| **Design / positioning pass** | Backlog | Content/UX, not infra |

## Suggested order

1. Merge PR #666 (CI + P2 SEO/nginx/catalog).
2. Monitor **`check-css-budget`** and Lighthouse on prod `/` after deploy.
3. If LCP regresses: prototype **admin CSS entry** (one vertical slice, e.g. `/admin` layout only).
4. Evaluate **prerender** only if search/social still miss content after `/og/*` and JSON-LD.

## Out of scope

- Full SSR framework migration.
- Replacing Tailwind with per-page CSS modules.
