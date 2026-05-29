# Security

How this repo handles common web risks. For vulnerability disclosure, see [SECURITY.md](../SECURITY.md).

## Transport and headers

Production serves the SPA and API through nginx with:

- `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`
- **HSTS** on the prod nginx config only
- **Content-Security-Policy** in [`nginx/security_headers.conf`](../nginx/security_headers.conf)

CSP currently allows `'unsafe-inline'` for scripts and styles so Vite dev HMR, Google Tag Manager, and inline bootstrapping work. Tightening CSP (nonces or hashes for built assets) is a planned hardening step; until then, XSS defenses rely on Vue escaping, minimal `v-html`, and DOMPurify on email previews.

## Authentication

- JWT access/refresh tokens (HS256) with bcrypt passwords
- HttpOnly cookies in production (`secure`, `SameSite=Lax`) plus optional Bearer header
- Refresh rotation and Redis token blacklist on logout
- Registration limited to `ALLOWED_EMAIL`; GitHub OAuth uses `GITHUB_ALLOWED_USERS`

## CSRF and CORS

The API uses `CORSMiddleware` with `allow_credentials=True`. In **production**:

- `CORS_ORIGINS` must list explicit origins (no `*`)
- Mutating `/api` requests that send the `access_token` cookie must include an `Origin` (or matching `Referer`) from `CORS_ORIGINS` — see [`server/app/core/csrf.py`](../server/app/core/csrf.py)

Public auth and feedback routes are exempt. Bearer-only clients (typical admin SPA with in-memory tokens) are unaffected.

## Rate limiting

Redis fixed-window limits on auth, feedback, and general API traffic — [`server/app/core/rate_limit.py`](../server/app/core/rate_limit.py).

## Input sanitization

| Surface | Mitigation |
|---------|------------|
| Email tool (server) | `html.escape` on body; length limits on subject/body |
| Email preview (client) | DOMPurify via [`sanitizeEmailHtml.ts`](../client/src/utils/sanitizeEmailHtml.ts) |
| AI chat | `sanitize_content` + message caps |
| File share uploads | Extension denylist; sanitized stored filenames |
| Downloads | Safe `Content-Disposition` via [`attachment_content_disposition`](../server/app/core/utils.py) |
| Vid download | YouTube host allowlist; yt-dlp `format` character allowlist; capability-gated |

## Admin tools and SSRF

**URL shortener:** Creating links requires auth. Public `/s/{code}` redirects to stored URLs — treat compromised admin accounts as a phishing risk.

**Vid download:** yt-dlp runs server-side only for users with the `vid-download` capability. URLs are restricted to known YouTube hosts.

## Secrets and CI

- Never commit `.env` (see [`.env.example`](../.env.example))
- Weekly Dependabot updates; [`security.yml`](../.github/workflows/security.yml) runs gitleaks, pip-audit, and npm audit

## Testing

- Default pytest uses SQLite — Postgres-only features need `POSTGRES_TEST_URL` and `@pytest.mark.postgres` (see [database.md](database.md#tests))
