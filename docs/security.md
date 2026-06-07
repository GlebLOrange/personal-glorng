# Security

How this repo handles common web risks. For vulnerability disclosure, see [SECURITY.md](../SECURITY.md).

## Transport and headers

Production serves the SPA and API through nginx with:

- `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`
- **HSTS** on the prod nginx config only
- **Content-Security-Policy** in [`nginx/security_headers.conf`](../nginx/security_headers.conf)

CSP currently allows `'unsafe-inline'` for scripts and styles so Vite dev HMR, Google Tag Manager, and inline bootstrapping work. Tightening CSP (nonces or hashes for built assets) is a planned hardening step; until then, XSS defenses rely on Vue escaping, minimal `v-html`, and DOMPurify on email previews.

**Dev caveat:** Lite mode (Vite → API on `:8000`, no nginx) skips CSP/HSTS. CSRF origin checks are production-only.

HTTPS termination is expected upstream of compose nginx (port 80 in-repo); `secure` cookies require HTTPS at the edge.

## Authentication

- JWT access/refresh tokens (HS256) with bcrypt passwords
- HttpOnly cookies in production (`secure`, `SameSite=Lax`) plus optional Bearer header
- Refresh rotation and Redis token blacklist on logout
- Open self-service registration with email verification; new users start with no tool permissions
- Password policy: 12+ chars, upper, lower, digit, special; common passwords rejected
- `ALLOWED_EMAIL` is seed-only for the bootstrap superuser; GitHub OAuth uses `GITHUB_ALLOWED_USERS`
- Users manage profile, password, email, and preferences via `/settings`; permissions are admin-only
- GitHub OAuth access tokens are **encrypted at rest** (Fernet, key derived from `JWT_SECRET`) — see [`core/fernet_secrets.py`](../server/app/core/fernet_secrets.py)

## CSRF and CORS

The API uses `CORSMiddleware` with `allow_credentials=True`. In **production**:

- `CORS_ORIGINS` must list explicit origins (no `*`)
- Mutating `/api` requests that send the `access_token` cookie must include an `Origin` (or matching `Referer`) from `CORS_ORIGINS` — see [`server/app/core/csrf.py`](../server/app/core/csrf.py)

Public auth and feedback routes are exempt. Bearer-only clients (typical admin SPA with in-memory tokens) are unaffected.

## Rate limiting

Redis fixed-window limits on auth, feedback, general API traffic, and search — [`server/app/core/rate_limit.py`](../server/app/core/rate_limit.py).

| Limiter | Limit | Routes |
|---------|-------|--------|
| Auth | 5/min | All `/api/auth/*` |
| API general | 30/min | Most public APIs |
| Search query | 30/min | `GET /api/search` |
| Search chat | 5/5min | `POST /api/search/chat` |
| Feedback | 5/5min | `POST /api/feedback` |

Rate-limit keys prefer nginx-set `X-Real-IP` over client-supplied `X-Forwarded-For`.

## Search and AI chat

Portfolio search uses Postgres full-text search with a visibility model:

| Visibility | Indexed content (examples) | Who can retrieve |
|------------|---------------------------|------------------|
| `PUBLIC` | Resume, public recipes | Anyone (keyword search + public AI chat) |
| `ADMIN` | Tasks, expenses, feedback bodies | Admin AI chat only (`ai-chat:write`) |

**Public endpoints** ([`server/app/routers/search.py`](../server/app/routers/search.py)):

- `GET /api/search` — keyword lookup over `PUBLIC` documents only (no LLM)
- `GET /api/search/config` — reports whether AI search is enabled and configured
- `POST /api/search/chat` — unauthenticated grounded AI chat; retrieval scoped to `PUBLIC` only

**Admin endpoint** ([`server/app/routers/tools/ai_chat.py`](../server/app/routers/tools/ai_chat.py)):

- `POST /api/tools/ai-chat` — requires `ai-chat:write`; retrieval includes `PUBLIC` + `ADMIN`

Both chat paths use retrieve-then-generate (`AiSearchService`): the LLM receives only indexed context blocks and is instructed to cite sources without inventing facts. Feature flags gate LLM usage:

- `AI_SEARCH_ENABLED` + `OPENAI_API_KEY` for public search chat
- `AI_CHAT_ENABLED` + `OPENAI_API_KEY` for admin AI chat

Client-side `VITE_*` flags hide UI only; server flags and auth are authoritative.

**Chat UI hardening:** message content is rendered as plain text (no `v-html`). Source citation links pass through [`safeUrl.ts`](../client/src/utils/safeUrl.ts) — relative paths and same-origin or external `https:` URLs only.

## Input sanitization

| Surface | Mitigation |
|---------|------------|
| Email tool (server) | `html.escape` on body; `sanitize_email_subject` blocks CRLF injection |
| Email preview (client) | DOMPurify via [`sanitizeEmailHtml.ts`](../client/src/utils/sanitizeEmailHtml.ts) |
| Email console backend | Logs metadata only (`to`, `subject`, byte sizes) — no HTML/token previews |
| AI chat / search | `sanitize_required_text` in [`core/text.py`](../server/app/core/text.py) + message caps |
| Search source links (client) | [`safeUrl.ts`](../client/src/utils/safeUrl.ts) blocks `javascript:` / `data:` hrefs |
| Tasks (admin + todobot) | Shared `TaskTextFields` validators |
| File share uploads | Extension denylist; sanitized stored filenames; daily expired-share cleanup |
| Downloads | Safe `Content-Disposition` via [`attachment_content_disposition`](../server/app/core/utils.py) |
| Vid download | YouTube host allowlist; yt-dlp `format` character allowlist; public with rate/concurrency limits |
| URL shortener | `HttpUrl` validation; private/localhost host blocklist on create |

## Public tools

**Recipes:** Read endpoints (list, tags, detail) are public and rate limited. Create, update, and delete require the `recipes:write` capability.

**URL shortener:** Creating short links is public (10 creates/hour/IP) with URL safety checks that block localhost and private-network targets. Public `/s/{code}` redirects to stored URLs — open redirects are an accepted risk for shorteners; your domain lends trust to destination sites.

**Vid download:** The download endpoint is public with strict limits (5 downloads/hour/IP, one concurrent download per IP, two server-wide). yt-dlp runs server-side; URLs are restricted to known YouTube hosts only.

## Secrets and CI

- Never commit `.env` (see [`.env.example`](../.env.example))
- Production startup validates strength of `JWT_SECRET`, `RABBITMQ_PASSWORD`, `POSTGRES_PASSWORD`, and the password embedded in `REDIS_URL` — see [`server/app/settings.py`](../server/app/settings.py)
- Weekly Dependabot updates; [`security.yml`](../.github/workflows/security.yml) runs gitleaks, pip-audit, and npm audit

## Risk register

Decisions for known risks. **Accept** = intentional tradeoff; **Mitigated** = controls in place; **Addressed** = fixed in code/docs.

| Priority | Risk | Status | Notes |
|----------|------|--------|-------|
| Medium | Public unauthenticated LLM (`POST /api/search/chat`) | **Accept** | Cost/abuse limited by 5/5min IP rate limit; feature flag + API key required; retrieval limited to `PUBLIC` index |
| Medium | Open registration | **Accept** | New users get zero permissions; email verification required; suitable for portfolio use |
| Medium | GitHub tokens in DB | **Addressed** | Encrypted at rest via Fernet; legacy plaintext decrypted on read until re-linked |
| Medium | CSP `unsafe-inline` | **Accept** | Documented tradeoff; Vue escaping + DOMPurify are primary XSS defenses |
| Low–Med | Public resource-heavy tools (vid-download, file-share) | **Mitigated** | Rate + concurrency limits |
| Low | Platform catalog info leak | **Accept** | Exposes service slugs/routes; acceptable for portfolio |
| Low | Client feature flags bypassable | **Mitigated** | Server auth, flags, and rate limits are authoritative |
| Low | Dev-lite API on all interfaces | **Accept** | Local development only; use firewall or bind to localhost |
| Low | No in-repo TLS | **Accept** | HTTPS expected at external reverse proxy |
| By design | Admin AI RAG scope | **Mitigated** | Requires `ai-chat:write`; DB-level visibility filter |

## Testing

- Default pytest uses SQLite — Postgres-only features need `POSTGRES_TEST_URL` and `@pytest.mark.postgres` (see [database.md](database.md#tests))
