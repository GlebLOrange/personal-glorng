# DevOps checklist

Inspection snapshot of edge, CI, backups, logging, and observability for this repo. Operator-owned items live on the VPS or SaaS dashboards; deferred items are intentional, not forgotten.

| Area | In-repo | Operator-owned | Deferred |
|------|---------|----------------|----------|
| **nginx** | Reverse proxy, SPA, API locations, prod CSP/HSTS ([`nginx/`](../../nginx/)) | Reload after cert/conf changes | — |
| **HTTPS** | Cloudflare overlay TLS ([`nginx.prod.cloudflare.conf`](../../nginx/nginx.prod.cloudflare.conf)); default prod is HTTP behind edge | Origin certs in `deploy/cloudflare/` | No certbot/ACME in-repo |
| **Cloudflare** | Real-IP restore, runbook ([Cloudflare](/operations/cloudflare)) | DNS, Full (strict), cache rules, host firewall allowlist | WAF rules only if abuse |
| **GitHub Actions** | CI, security, nightly, pre-release, optional Sentry upload | Repo secrets (`SENTRY_*`) | Full CD to VPS |
| **Backups** | `make backup`, cron install, Mongo/Redis/media (+ optional Postgres), optional `BACKUP_OFFSITE_CMD` | Cron on host, offsite target, restore drills | Managed object-storage product |
| **Logging** | JSON Loguru stderr, optional Mongo/ES app logs, prod `json-file` rotation | `docker logs` / host retention | Loki/Fluent Bit shipper |
| **Prometheus** | — | — | No scrape stack; health via `/api/health` + `/api/ready` |
| **Grafana** | — | — | No dashboards; use Sentry + logs |
| **Sentry** | Server + client SDKs; vite plugin when token set; optional [`sentry-release`](../../.github/workflows/sentry-release.yml) workflow | DSN + auth token secrets; release string alignment | Celery traces parity with FastAPI |

## Quick links

- [Deployment](/operations/deployment)
- [Cloudflare](/operations/cloudflare)
- [Backup & restore](/operations/backup-restore)
- [Security](/reference/security)
- [Testing](/reference/testing)
