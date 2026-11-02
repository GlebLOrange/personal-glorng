# Frontend

Vue 3 SPA served by Vite in development and built into static assets for production nginx.

## Stack

- Vue 3, TypeScript, Vite
- Pinia (auth, preferences)
- Vue Router
- Tailwind CSS
- Vitest + Playwright (E2E)

Source: [`client/`](../../client/).

## Routing

[`client/src/router/index.ts`](../../client/src/router/index.ts) defines public, auth, and admin routes.

| Area | Paths | Notes |
|------|-------|-------|
| Public | `/`, `/tools`, `/recipes`, `/news`, … | Portfolio and guest tools |
| Auth | `/login`, `/settings`, … | `meta.requiresAuth` guards |
| Admin | `/admin`, `/admin/*` hub routes | Capability / superuser checks via `usePermissions` |
| Tools | `/tools`, `/tasks`, `/expenses`, … | Public catalog + capability-gated top-level tools |

Navigation guards restore session from cookies/storage and enforce `requiresSuperuser` on `/admin/users`.

## Auth state

[`client/src/stores/auth.ts`](../../client/src/stores/auth.ts) — login, refresh, logout, permission list. Tokens may be held in memory (Bearer) or HttpOnly cookies depending on environment.

Session restore and refresh logic: [`client/src/utils/authSession.ts`](../../client/src/utils/authSession.ts).

## Platform catalog

Admin dashboard tools come from `GET /api/platform/services`. Client mirror:

- [`client/src/platform/services.ts`](../../client/src/platform/services.ts)
- Parity test: [`client/src/platform/services.parity.test.ts`](../../client/src/platform/services.parity.test.ts)

Capability gating in UI: [`client/src/composables/usePermissions.ts`](../../client/src/composables/usePermissions.ts).

## CSS bundle

Single global Tailwind bundle (`main.css` → `index-*.css`). Audit, budgets, and follow-ups: [Frontend CSS audit](/guide/frontend-css-audit). Production `build:check` runs `check-css-budget.mjs` (132 KB raw cap on entry CSS).

## Feature flags

Server flags are authoritative. Client `VITE_*` flags only hide UI:

- [`client/src/utils/featureFlags.ts`](../../client/src/utils/featureFlags.ts)
- AI chat/search, Firebase, Sentry toggles

## API calls

- Composables: `useApiAction`, `useCachedApi`, `streamingPost` (SSE for search chat)
- Dev proxy: `VITE_API_PROXY_TARGET` → API on :8000

## Security helpers (client)

| Utility | Purpose |
|---------|---------|
| [`safeUrl.ts`](../../client/src/utils/safeUrl.ts) | Safe hrefs for citations and redirects |
| [`safeImageSrc.ts`](../../client/src/utils/safeImageSrc.ts) | Image URL allowlist |
| [`sanitizeEmailHtml.ts`](../../client/src/utils/sanitizeEmailHtml.ts) | DOMPurify for email preview |

## Design system

Shared UI primitives live in `client/src/components/ui/` (`BaseButton`, `BaseInput`, `BaseDrawer`, …). Coding standards for Vue/TS: path-triggered stubs in [`.cursor/rules/`](../../.cursor/rules/) and full guidance in [`.cursor/skills/`](../../.cursor/skills/) (`vue` and `client-ui`).

**2026-10-31 — Tool chrome + button/input bar:** `.page-tool-body` centers children; `CollapsibleUsageGuide` stays within `.page-tool-actions` width. URL shortener hides clicks in the UI only (server still increments). Sitewide: every button gets an action-matching SVG (including calculator keys and ghost chrome; already icon-only controls stay as-is); inputs use visible labels, not aria/placeholder-only names.

**2026-10-27 — Utils pills → full PageShell:** On `/tools`, every visible utils tool is a pill (order: weather, ai chat, then the remainder). Each opens a standalone public `PageShell` page (tools breadcrumb, back to `/tools`, `max-w-5xl`) — not `AdminPageLayout` and not the old `SmallToolsWindow` / `/_small-tools` shell. Content and server stay card spoilers. Supersedes the same-day compact-window note and the 2026-10-26 lines that limited the compact window to four peers.

**2026-10-26 — Tools utils static + router shell:** Superseded 2026-10-27 — utils no longer use `SmallToolsWindow`. Content and server groups stay open `<details>` spoilers with tiles; admin/edit tiles only for a superuser. Route `meta.requiresAuth` for `/vid-download` and `/tools/send-email` is unchanged.

**2026-10-26 — Tools hub vs tabs:** Superseded 2026-10-27 for utils. Category buckets (utils / content / server) remain for the `/tools` catalog. Utils open as full `PageShell` pages; content and server catalog tiles stay cards.

**2026-09-23 — Homepage hire path:** Public `/` section order is about → experience → projects → skills → contacts ([`portfolioSections.ts`](../../client/src/constants/portfolioSections.ts)). In-page jumps sit under the hero, not in the site header. The header stays visible on `/` only (hide-on-scroll remains elsewhere).

## Local commands

```bash
cd client
npm run dev
npm run lint
npm run test
npm run build:check
npm run e2e          # needs API + preview server
npm run analyze      # bundle stats → dist/stats.html
```

## Related

- [API & tools](/reference/api-tools) — endpoints and capabilities
- [Security](/reference/security) — XSS, CSP, client hardening
- [Development](/guide/development) — ports and dev-lite workflow
