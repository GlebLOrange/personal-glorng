# DevOps checklist

Inspection snapshot of edge, CI, backups, logging, and observability for this repo. Operator-owned items live on the VPS or SaaS dashboards; deferred items are intentional, not forgotten.

## Development vs production (GitHub / CI/CD)

**During active development, merge gates and production hardening are turned off.** Workflows may still run for signal, but they must not block day-to-day work. Enable and verify the production column before a real production cutover.

| Area | Development (now) | Before production — turn on / verify |
|------|-------------------|-------------------------------------|
| **Branch ruleset** `main-protection` | **Disabled** (`enforcement: disabled`). Rules are pre-configured but not enforced. | Set enforcement to **Active**. Requires PR to `main`, blocks force-push/delete, requires status checks `ci-ok` + `gitleaks`. |
| **Required status checks** | Not enforced | Require **`ci-ok`** (aggregator in [`ci.yml`](../../.github/workflows/ci.yml)) and **`gitleaks`** ([`security.yml`](../../.github/workflows/security.yml)). Confirm exact check names after a green PR. |
| **Actions workflow permissions** | Prefer default **read** for `GITHUB_TOKEN`; do not let Actions approve PRs | Keep `default_workflow_permissions=read` and `can_approve_pull_request_reviews=false` (already the intended prod posture). |
| **CI gate** [`ci.yml`](../../.github/workflows/ci.yml) | Runs on PRs/`main` (path-filtered); failures are advisory while ruleset is off | With ruleset active, **`ci-ok`** is a hard merge gate. |
| **Security** [`security.yml`](../../.github/workflows/security.yml) | gitleaks on PR/push; pip/npm audit on schedule or lockfile changes | Keep enabled; require **`gitleaks`** on merge when ruleset is active. |
| **Nightly** [`nightly.yml`](../../.github/workflows/nightly.yml) | Optional redis integration (schedule + manual) | Leave on; treat failures as ops signal before release. |
| **Pre-release** [`pre-release.yml`](../../.github/workflows/pre-release.yml) | Manual only | Run once before each production deploy (compose + nginx smoke). |
| **Sentry release** [`sentry-release.yml`](../../.github/workflows/sentry-release.yml) | Skips without secrets | Set `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT`; align release strings on deploy. |
| **Docs Pages** [`docs-pages.yml`](../../.github/workflows/docs-pages.yml) | Optional (path-filtered deploy) | Enable GitHub Pages → GitHub Actions if publishing the handbook. |
| **Dependabot** [`.github/dependabot.yml`](../../.github/dependabot.yml) | Weekly PRs (uv, npm, Actions, Docker) | Review/merge regularly; do not disable for prod. |
| **Repo secrets** | Minimal / unset OK for local | Production host `.env` + optional Actions secrets (`SENTRY_*`); never commit `.env`. |
| **Full CD to VPS** | Not in-repo | Deferred — deploy remains operator-run (`make prod` / Cloudflare overlay). |

Re-enable the ruleset (GitHub → **Settings → Rules → main-protection → Enforce**), or:

```bash
gh api --method PUT repos/GlebLOrange/personal-glorng/rulesets/16927789 \
  -f enforcement=active
# Prefer a full PUT that preserves rules; see GitHub ruleset UI if unsure.
```

Workflow inventory and local test tiers: [Testing](/reference/testing). Deploy runbook: [Deployment](/operations/deployment).

## Surface area

| Area | In-repo | Operator-owned | Deferred |
|------|---------|----------------|----------|
| **nginx** | Reverse proxy, SPA, API locations, prod CSP/HSTS ([`nginx/`](../../nginx/)) | Reload after cert/conf changes | — |
| **HTTPS** | Cloudflare overlay TLS ([`nginx.prod.cloudflare.conf`](../../nginx/nginx.prod.cloudflare.conf)); default prod is HTTP behind edge | Origin certs in `deploy/cloudflare/` | No certbot/ACME in-repo |
| **Cloudflare** | Real-IP restore, runbook ([Cloudflare](/operations/cloudflare)) | DNS, Full (strict), cache rules, host firewall allowlist | WAF rules only if abuse |
| **GitHub Actions** | CI, security, nightly, pre-release, optional Sentry upload — **merge gates off in development** (see table above) | Repo secrets (`SENTRY_*`); enable ruleset before production | Full CD to VPS |
| **Backups** | `make backup`, cron install, Mongo/Redis/media (+ optional Postgres), optional `BACKUP_OFFSITE_CMD` | Cron on host, offsite target, restore drills | Managed object-storage product |
| **Logging** | Quiet dev defaults (`LOG_REQUESTS=false`, persist `WARNING+`); prod request logs on; JSON Loguru stderr + optional Mongo/ES; prod `json-file` rotation | `docker logs` / host retention | Loki/Fluent Bit shipper |
| **Prometheus** | — | — | No scrape stack; health via `/api/health` + `/api/ready` |
| **Grafana** | — | — | No dashboards; use Sentry + logs |
| **Sentry** | Server + client SDKs; vite plugin when token set; optional [`sentry-release`](../../.github/workflows/sentry-release.yml) workflow | DSN + auth token secrets; release string alignment | Celery traces parity with FastAPI |

## Quick links

- [Deployment](/operations/deployment)
- [Cloudflare](/operations/cloudflare)
- [Backup & restore](/operations/backup-restore)
- [Security](/reference/security)
- [Testing](/reference/testing)
- [Contributing](/guide/contributing)
