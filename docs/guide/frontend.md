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
| Auth | `/login`, `/register`, `/settings`, … | `meta.requiresAuth` guards |
| Admin | `/admin`, `/admin/tools/*` | Capability checks via `usePermissions` |

Navigation guards restore session from cookies/storage and enforce `requiresSuperuser` on `/admin/users`.

## Auth state

[`client/src/stores/auth.ts`](../../client/src/stores/auth.ts) — login, refresh, logout, permission list. Tokens may be held in memory (Bearer) or HttpOnly cookies depending on environment.

Session restore and refresh logic: [`client/src/utils/authSession.ts`](../../client/src/utils/authSession.ts).

## Platform catalog

Admin dashboard tools come from `GET /api/platform/services`. Client mirror:

- [`client/src/platform/services.ts`](../../client/src/platform/services.ts)
- Parity test: [`client/src/platform/services.parity.test.ts`](../../client/src/platform/services.parity.test.ts)

Capability gating in UI: [`client/src/composables/usePermissions.ts`](../../client/src/composables/usePermissions.ts).

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

Shared UI primitives live in `client/src/components/ui/` (`BaseButton`, `BaseInput`, `BaseDrawer`, …). Coding standards for Vue/TS: [`.cursor/rules/`](../../.cursor/rules/) (frontend and design-system rules).

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
