# Intentional public-surface gaps

Round 1 first-visitor sessions flagged missing pricing, terms, and signup. These are **by design** for this portfolio — not accidental 404s to “fix” with new product routes.

| Gap | Public behavior | Why |
|-----|-----------------|-----|
| `/pricing` | 404 (no route) | No packaged pricing; hire/contract via inquiry |
| `/terms` | 404 (no route) | No public product ToS; see `/privacy` |
| Registration / signup | Disabled (`POST /api/auth/register` → 403); login is operator-only | Owner-provisioned accounts only |

Do **not** add public pricing/terms routes or enable self-registration unless product explicitly decides to.

Canonical write-up: [`docs/reference/security.md`](../../docs/reference/security.md) — *Public product surface (intentional gaps)*.
