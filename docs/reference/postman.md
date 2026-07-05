# Postman

Use Postman against a **development** API. OpenAPI is disabled in production (`APP_ENV=production`).

## Prerequisites

```bash
make dev-lite   # API on http://127.0.0.1:8000
```

Confirm the spec loads:

```bash
curl -sf http://127.0.0.1:8000/api/openapi.json | head -c 200
```

Swagger UI (same stack): [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs).

## Import the collection

1. Postman → **Import** → **Link**.
2. URL: `http://127.0.0.1:8000/api/openapi.json`
3. Import as a collection (name will match the FastAPI app title).

Re-import after router changes to pick up new endpoints. For an offline snapshot:

```bash
curl -sf http://127.0.0.1:8000/api/openapi.json -o /tmp/glorng-openapi.json
```

Then Import → File. Do not commit generated JSON to git — it goes stale quickly.

## Environment

Template in [`postman/environments/glorng-local.environment.yaml`](../../postman/environments/glorng-local.environment.yaml). Postman **Local View** loads everything under `postman/` (see [`.postman/resources.yaml`](../../.postman/resources.yaml)).

| Variable | Example | Purpose |
|----------|---------|---------|
| `base_url` | `http://127.0.0.1:8000` | API root (no trailing slash) |
| `admin_email` | `admin@admin.admin` | Login body |
| `admin_password` | *(your `SEED_PASSWORD`)* | Login body — never commit real values |
| `access_token` | *(set by script)* | Bearer auth for admin routes |
| `refresh_token` | *(set by script)* | Token refresh |
| `webhook_task_secret` | *(from `WEBHOOK_SECRETS`)* | HMAC for manual webhook requests |

Production/staging: duplicate the environment and set `base_url` to `https://your-domain`.

## Authentication

Admin routes need **Bearer** `{{access_token}}` plus capability permissions. Cookies are optional in Postman; Bearer is simpler.

### Login request

`POST {{base_url}}/api/auth/login`

```json
{
  "email": "{{admin_email}}",
  "password": "{{admin_password}}"
}
```

**Tests** tab (save tokens to the active environment):

```javascript
const body = pm.response.json();
if (body.access_token) {
  pm.environment.set("access_token", body.access_token);
}
if (body.refresh_token) {
  pm.environment.set("refresh_token", body.refresh_token);
}
```

### Collection auth

Collection → **Authorization** → Type **Bearer Token** → Token `{{access_token}}`.

Individual public folders (health, resume, public search) can override to **No auth**.

### Refresh on 401

`POST {{base_url}}/api/auth/refresh`

```json
{
  "refresh_token": "{{refresh_token}}"
}
```

Use the same Tests script to update `access_token`. Auth routes are rate-limited to **5/min per IP** (fail closed if Redis is down) — see [Security](/reference/security).

## What OpenAPI covers

Imported automatically from `/api/openapi.json`:

- All `/api/*` JSON routes registered on the FastAPI app
- Tags from [`server/app/openapi.py`](../../server/app/openapi.py) (auth, tasks, expenses, search, …)
- Bearer security scheme on capability-gated admin tools

## What to add manually

These are **not** in OpenAPI or need custom Postman setup:

| Route | Why manual |
|-------|------------|
| `GET /s/{code}` | Short-link redirect — not under `/api` |
| `GET /f/{code}` | File download by share code |
| `POST /api/webhooks/{slug}` | HMAC header `X-Glorng-Signature: sha256=<hex>` — see [Integration automation](/reference/integration-automation#inbound-webhooks) |
| `POST /api/donations/webhook` | Stripe signature header |
| `POST /api/search/chat` | SSE stream — Postman shows stream chunks; use curl or client for full SSE testing |
| `POST /api/tools/ai-chat` | May stream — same caveat |

Suggested extra folder: **Webhooks & redirects** with pre-request scripts for HMAC:

```javascript
const secret = pm.environment.get("webhook_task_secret");
const body = pm.request.body.raw;
const sig = CryptoJS.HmacSHA256(body, secret).toString(CryptoJS.enc.Hex);
pm.request.headers.upsert({ key: "X-Glorng-Signature", value: "sha256=" + sig });
```

(Postman includes CryptoJS in pre-request scripts.)

## Rate limits

Postman bursts can hit limits quickly. Notable caps:

| Route | Limit |
|-------|-------|
| `/api/auth/*` | 5/min |
| Most public APIs | 30/min |
| `POST /api/feedback` | 5/5min |
| `POST /api/search/chat` | 5/5min |

Full table: [Security — rate limiting](/reference/security#rate-limiting).

## Repo layout

```
postman/
  environments/glorng-local.environment.yaml   # template vars (no secrets)
.postman/resources.yaml                        # Local View workspace id
```

Commit collections and environment **templates** only. Keep passwords and webhook secrets in Postman local vault or `.env`, not in git.

## Related

- [API & tools](/reference/api-tools) — endpoint catalog and capabilities
- [Integration automation](/reference/integration-automation) — curl examples, n8n, webhooks
- [Configuration](/reference/configuration) — env vars for features and secrets
