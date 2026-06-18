# Integration automation

How to connect external tools (shell scripts, n8n, Huginn, cron) to gLOrng without changing application code.

See also [api-tools.md](api-tools.md) for the full endpoint catalog and [integration webhooks](#inbound-webhooks) below.

## Discover services

```bash
BASE=https://your-domain
curl -s "$BASE/api/platform/services" | jq '.services[] | {slug, capabilities, public}'
curl -sf "$BASE/api/ready"
```

## JWT auth for admin tools

Admin routes under `/api/tools/*` require a Bearer token and capability permissions (bootstrap admin has `platform:superuser`).

### Login and call

```bash
BASE=https://your-domain
EMAIL=admin@admin.admin
PASS='your-password'

TOKENS=$(curl -s -X POST "$BASE/api/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}")

ACCESS=$(echo "$TOKENS" | jq -r .access_token)
REFRESH=$(echo "$TOKENS" | jq -r .refresh_token)

curl -s "$BASE/api/auth/me" -H "Authorization: Bearer $ACCESS" | jq '.permissions'

curl -s -X POST "$BASE/api/tools/tasks" \
  -H "Authorization: Bearer $ACCESS" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "From automation",
    "scheduled_at": "2026-06-08T10:00:00Z",
    "description": "Created via curl"
  }' | jq .
```

### Refresh before expiry

```bash
ACCESS=$(curl -s -X POST "$BASE/api/auth/refresh" \
  -H 'Content-Type: application/json' \
  -d "{\"refresh_token\":\"$REFRESH\"}" | jq -r .access_token)
```

Production note: Bearer-only clients skip CSRF. Auth endpoints are limited to **5 requests/minute per IP**.

## Example: monthly expense export

```bash
MONTH=$(date +%Y-%m)
curl -s "$BASE/api/tools/expenses/export?month=$MONTH" \
  -H "Authorization: Bearer $ACCESS" \
  -o "expenses-$MONTH.csv"
```

## Example: poll audit log after mutations

```bash
curl -s "$BASE/api/tools/audit?category=domain&per_page=20" \
  -H "Authorization: Bearer $ACCESS" | jq '.items[] | {action, occurred_at}'
```

## Public endpoints (no login)

| Use case | Endpoint |
|----------|----------|
| Keyword search | `GET /api/search?q=...` |
| AI chat (SSE) | `POST /api/search/chat` |
| Weather / time | `GET /api/time-date-weather-location/lookup/{city}` |
| Visitor feedback | `POST /api/feedback` |
| Short URL | `POST /api/tools/url-shortener` |
| Resume JSON | `GET /api/resume` (static public profile data) |
| GitHub public repos | `GET /api/github/repos` |

Rate limits apply (typically 30/min; see [security.md](security.md)).

## Inbound webhooks

When `WEBHOOK_SECRETS` is configured, external systems can POST signed payloads without JWT.

**Endpoint:** `POST /api/webhooks/{slug}`

**Header:** `X-Glorng-Signature: sha256=<hex>` where the hex is `HMAC-SHA256(secret, raw_body)`.

**Built-in slugs:**

| Slug | Action |
|------|--------|
| `task-create` | Creates a task (same fields as `POST /api/tools/tasks`) |
| `feedback` | Creates feedback (same fields as `POST /api/feedback`) |
| `ping` | Records an audit event; returns `{ "ok": true }` |

Example (task-create):

```bash
SECRET='your-task-create-secret'
BODY='{"title":"Deploy check","scheduled_at":"2026-06-08T09:00:00Z"}'
SIG=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $2}')

curl -s -X POST "$BASE/api/webhooks/task-create" \
  -H 'Content-Type: application/json' \
  -H "X-Glorng-Signature: sha256=$SIG" \
  -d "$BODY"
```

Configure secrets in `.env`:

```env
WEBHOOK_SECRETS={"task-create":"replace-me","feedback":"replace-me","ping":"replace-me"}
```

## Donations

When `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` are set:

- `POST /api/donations/checkout` — returns a Checkout Session URL (public, rate-limited)
- `POST /api/donations/webhook` — Stripe-signed events (`checkout.session.completed` notifies admin via Telegram)

PayPal and Patreon support use the configured external links from `GET /api/donations/config`.

Local testing with [Stripe CLI](https://stripe.com/docs/stripe-cli):

```bash
stripe listen --forward-to localhost:8000/api/donations/webhook
```

## n8n workflow sketch

1. **Schedule Trigger** (e.g. daily 08:00)
2. **HTTP Request** — POST `/api/auth/login`, store `access_token` in workflow static data
3. **HTTP Request** — GET `/api/tools/tasks` with Bearer header
4. **HTTP Request** — GET `/api/time-date-weather-location/lookup/Warsaw` (no auth)
5. **Merge** — combine into digest; optional Telegram or email node

For webhook-driven flows, use n8n **Webhook** node → sign with `Crypto` node (HMAC SHA256) → POST to `/api/webhooks/task-create`.

Token refresh: add a branch that POSTs `/api/auth/refresh` when a tool call returns 401.

## GitHub API (linked account)

After linking GitHub in admin settings:

```bash
curl -s "$BASE/api/auth/github/repos" -H "Authorization: Bearer $ACCESS" | jq .
curl -s "$BASE/api/auth/github/issues" -H "Authorization: Bearer $ACCESS" | jq .
```

Public portfolio repos (no login): `GET /api/github/repos` — uses `GITHUB_PUBLIC_USERNAME` or the first entry in `GITHUB_ALLOWED_USERS`.

## Related docs

- [api-tools.md](api-tools.md) — capabilities and UI routes
- [platform.md](platform.md) — channels and service pattern
- [security.md](security.md) — rate limits and auth model
