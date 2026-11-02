# Ops (stacks, DB, backups)

Run existing Make targets for stacks, database maintenance, and backups. Do **not** invent shell logic, Compose flags, or new scripts.

User request (after the command):

```text
$ARGUMENTS
```

Treat `$ARGUMENTS` as **one** name (first word only). Empty or unknown: print the menu below and stop. Do not guess.

## Rules

- Work from the **repo root** only.
- Do **not** edit application code, `.env`, Docker Compose files, or Makefile targets.
- Do **not** add Compose flags or wrap Make in custom scripts.
- Do **not** run tests.
- Do **not** commit, push, or open a PR.
- Map only the names listed below to Make targets (except `maintain` → follow [`.cursor/commands/maintain.md`](maintain.md)). Anything else → menu and stop.

## Menu (print when empty / unknown)

```text
/ops <name>

Start (background terminal; report URL; do not wait for exit):
  dev | lite     → make dev          (Vite: /ops client)
  client         → make dev-lite-client
  docker         → make dev-docker
  search         → make dev-search
  postgres       → make dev-postgres
  worker         → make dev-worker
  bot            → make dev-bot
  full           → make dev-full
  rebuild        → make rebuild
  ultra-infra    → make dev-ultra-lite-infra
  ultra-server   → make dev-ultra-lite-server
  logs           → make logs
  bot-logs       → make bot-logs

One-shot (wait; report success or error):
  backup         → make backup       (dump + verify + rotate + migrate)
  maintenance    → make maintenance  (backup stale check only)
  sync           → make sync         (calendar sync queue, one batch)
  cleanup        → make cleanup      (old tasks / shares / health results)
  logs-rotate    → make logs-rotate  (truncate Docker json-file logs)
  db-init | migrate → make db-init
  seed           → make seed-db      (maintenance seed; prefer /admin/db-maintenance)
  reindex        → make reindex-search
  db-check       → make db-check
  db-current     → make db-current
  maintain       → follow /maintain checklist (updates, CI, reviews, then jobs)

Ask once before running:
  down           → make down
  reset          → make db-reset     (drops volumes)
  downgrade      → make db-downgrade
  backup-install → make backup-install  (writes cron)
  pull-prod      → make db-pull-prod    (do not set CONFIRM_PROD_PULL unless user confirmed)
  docker-maintain → make docker-maintain  (prune containers/images/build cache; no volumes)
  update         → make update       (compose pull + up --build; OPS_STACK=lite|prod)
  prod           → make prod
  prod-cloudflare → make prod-cloudflare
```

## Start (background)

For these names, run the Make target in a **background** terminal. Report the relevant URL from docs (e.g. http://localhost, http://localhost:3000, API docs). Do **not** wait for the process to exit.

| Name | Command | Note |
|------|---------|------|
| `dev`, `lite` | `make dev` | After start, say Vite needs a second `/ops client` |
| `client` | `make dev-lite-client` | |
| `docker` | `make dev-docker` | |
| `search` | `make dev-search` | |
| `postgres` | `make dev-postgres` | |
| `worker` | `make dev-worker` | |
| `bot` | `make dev-bot` | |
| `full` | `make dev-full` | |
| `rebuild` | `make rebuild` | |
| `ultra-infra` | `make dev-ultra-lite-infra` | |
| `ultra-server` | `make dev-ultra-lite-server` | |
| `logs` | `make logs` | |
| `bot-logs` | `make bot-logs` | |

## One-shot (wait)

Run, wait for exit, then report success or the error output.

| Name | Command | Note |
|------|---------|------|
| `backup` | `make backup` | Also migrates after a successful dump |
| `maintenance` | `make maintenance` | Stale-check only (`--check-stale`) |
| `sync` | `make sync` | One calendar sync batch (max 10); needs running `server` |
| `cleanup` | `make cleanup` | Old tasks, expired shares, health results |
| `logs-rotate` | `make logs-rotate` | Truncate json-file logs; `make logs` still follows |
| `db-init`, `migrate` | `make db-init` | |
| `seed` | `make seed-db` | Maintenance seed (CLI alias); prefer admin job when Turnstile is up |
| `reindex` | `make reindex-search` | |
| `db-check` | `make db-check` | |
| `db-current` | `make db-current` | |
| `maintain` | follow `/maintain` | Preflight checklist then admin/Make jobs; do not invent shell |

## Confirm once (destructive / prod)

Ask the user once. Run only after an explicit yes.

| Name | Command | Warn |
|------|---------|------|
| `down` | `make down` | Stops containers |
| `reset` | `make db-reset` | Drops volumes |
| `downgrade` | `make db-downgrade` | Alembic -1 |
| `backup-install` | `make backup-install` | Writes crontab |
| `pull-prod` | `make db-pull-prod` | Do **not** set `CONFIRM_PROD_PULL` unless the user just confirmed; script requires it in `.env` or env |
| `docker-maintain` | `make docker-maintain` | Prunes stopped containers, dangling images, build cache; never volumes |
| `update` | `make update` | Pull + recreate (`OPS_STACK=lite` default or `prod`); short blip |
| `prod` | `make prod` | Production compose |
| `prod-cloudflare` | `make prod-cloudflare` | Production + Cloudflare overlay |

## Final message

```text
## Ops result
- Name: …
- Command: …
- Status: started (background) | ok | failed | cancelled | menu
- Notes: …
```
