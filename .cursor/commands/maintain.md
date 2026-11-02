# Maintain (preflight + admin jobs)

Run this checklist **before** kicking off maintenance jobs. Do **not** invent shell automation for DRY/sanitize/bugcheck. Host Docker jobs (`update`, `docker-maintain`, `logs-rotate`) stay Make-only — see `/ops`.

User request (after the command):

```text
$ARGUMENTS
```

## Rules

- Work from the **repo root** only.
- Do **not** commit, push, or open a PR unless the user already asked in this chat.
- Do **not** seed production without an explicit yes.
- Stop and report if a hard step fails (fetch/auth, red CI you cannot explain).

## Ordered steps

### 1. Updated?

```bash
git fetch origin
git status -sb
git rev-list --left-right --count HEAD...origin/main
gh pr list --state open --label dependencies --limit 10
```

Report how far behind/ahead of `origin/main` you are and any open Dependabot PRs. Do **not** auto-merge.

### 2. CI

If on a PR branch:

```bash
gh pr checks
```

Otherwise summarize the latest Actions run on the branch. Call out red checks.

### 3. Plan

List which admin jobs to run from `/admin/db-maintenance` (or Make aliases):

| Job | When |
|-----|------|
| `backup` | Host script ready (`DB_MAINTENANCE_*`); dump + migrate |
| `stale` | Check `LAST_SUCCESS` freshness |
| `sync` | Drain Google Calendar sync queue (one batch) |
| `cleanup` | Old tasks, expired shares, health results |
| `seed` | Non-prod (or `MAINTENANCE_SEED_ENABLED=true`) + user confirmed |

Ask once if seed is in the plan.

### 4. Bugcheck / security

If there are uncommitted changes or an open PR with code delta: launch Bugbot and Security Review subagents on that diff. If no code delta: skip and note “no code delta”.

### 5. Logs / DRY / sanitize

Inspect using the seed map in [`docs/specs/manager-maintenance-themes.md`](../../docs/specs/manager-maintenance-themes.md) and [`docs/operations/logging.md`](../../docs/operations/logging.md). Recommend only real gaps. Do not invent scripts for DRY or sanitize.

### 6. Maintain db

Run or instruct the chosen jobs via the admin panel (Turnstile) or Make (`make backup`, `make maintenance`, `make sync`, `make cleanup`, `make seed-db`). Prefer admin when Turnstile is configured.

After each admin job finishes, the API emails `ALLOWED_EMAIL` with what was done.

## Final message

```text
## Maintain result
- Updated: …
- CI: …
- Plan: …
- Bugcheck/security: ran | skipped (no code delta)
- Logs/DRY/sanitize: …
- Jobs: …
- Notes: …
```
