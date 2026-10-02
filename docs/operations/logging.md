# Audit logs and app logs

Audit events and application logs are two different stores. Keep that split. See [Architecture — Observability](/guide/architecture#observability).

## App logs

Structured logs go to stderr (`make logs`) and optionally to Mongo `app_logs` via [`app_log_persist.py`](../../server/app/core/app_log_persist.py).

Probe traffic is excluded in both request logging and Mongo persistence via shared [`PROBE_LOG_SKIP_PATHS`](../../server/app/core/probe_paths.py): `/api/health` and `/api/ready`. Failures logged without a probe `path` still persist.

Retention and knobs: [Security — Application log persistence](/reference/security#application-log-persistence), [Configuration](/reference/configuration).

## Audit logs

Written only through `AuditService.record`. Mongo `audit_events` is the source of truth. No TTL. Review at `/admin/audit-logs`.

## Related

- [Security — Application log persistence](/reference/security#application-log-persistence)
- [Architecture — Observability](/guide/architecture#observability)
- [Configuration](/reference/configuration)
