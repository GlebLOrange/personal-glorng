# Spec: Platform hardening (current state)

**Status:** Program largely shipped. This page is a status checklist, not a how-to. Operator procedures live on [Backup & restore](/operations/backup-restore), [Security](/reference/security), [Testing](/reference/testing), and [Deployment](/operations/deployment).

## Decisions (locked)

| # | Decision | Choice |
|---|----------|--------|
| D1 | JWT `session_version` migration | **Fail closed** — missing `sv` ⇒ invalid token |
| D2 | XML hardening | **`defusedxml`** (parser-level) |
| D3 | Settings / secrets | **Process env first** (dotenv for local/dev; Docker secrets supported) |
| D4 | Phase 5 admin split | **Skip optional admin page split** — a11y + remove dead client `TokenResponse` only |

## Phase status (re-checked against tree)

| Phase | Theme | Status | Evidence |
|-------|--------|--------|----------|
| 1 | Mongo backup & restore | **Done** | `scripts/db_maintenance.sh`, [Backup & restore](/operations/backup-restore), `make backup` |
| 2 | Session revocation (`sv`) | **Done** | `User.session_version`; JWT claim `sv`; fail-closed matcher in `security.py` / `deps.py`; bumps on password reset/change and email change |
| 3 | Attack surface | **Done** | DNS-aware `url_safety`; Stripe webhook fail-closed rate limit; `defusedxml` via `xml_security.py`; body-log skip/cap + prod forbids `LOG_REQUEST_BODIES` |
| 4 | Ops / CI trust | **Done** | Testing docs aligned; Dependabot covers `/docs`, Actions, Docker, uv/npm; prod compose `no-new-privileges` + log rotation; Settings process-env order (D3) |
| 5 | Frontend a11y / debt | **Done** | Dropdown/`RecipeCard` accessible names + action stop-propagation; client dead `TokenResponse` removed (server auth `TokenResponse` remains for refresh) |

## Success list

| Criterion | Status |
|-----------|--------|
| Mongo dump + documented restore path | Met |
| Credential change invalidates other-device tokens (`sv`) | Met |
| URL safety rejects private/link-local (incl. DNS) | Met |
| Stripe donation webhook fail-closed rate-limited | Met |
| XML extraction rejects DTD/entity expansion (`defusedxml`) | Met |
| Request-body logging capped / skips multipart; forbidden in prod | Met |
| Testing docs match automation; Dependabot covers docs/Actions/Docker | Met |
| Critical menu/card a11y fixes landed | Met |

## Related defaults (security posture)

- `UNTRUSTED_URL_TOOLS_ENABLED` defaults to **`false`** (yt-dlp, file-share, outbound health-checker not mounted) — [Configuration](/reference/configuration)
- Cloudflare real-IP / origin allowlist: [Cloudflare](/operations/cloudflare)

## Remaining / deferred (not blocking)

| Item | Notes |
|------|--------|
| Broader `limit=10_000` cursor/batch sweeps | Perf, not security |
| Extra compound Mongo indexes / atomic counters | Nice-to-have |
| Shared `httpx.AsyncClient` | Perf |
| Full CodeQL/Trivy/SBOM expansion | After Dependabot maturity |
| Origin IP allowlist (host firewall) | Operator-owned — documented under Cloudflare |

## Out of scope (unchanged)

Full frontend redesign, cloud vault product, compose topology rewrite, Playwright expansion beyond existing smokes.
