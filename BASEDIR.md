# PR #419 improvement suggestions

Review target: [Cursor/disable sentry dev](https://github.com/GlebLOrange/personal-glorng/pull/419) (`cursor/disable-sentry-dev` → `main`).

Verdict: the Sentry change is the right shape (DSN required; `development`/`test` also need `SENTRY_ENABLED=true`) and the new matrix test covers the main env cases. The deployment runbook rewrite is useful but larger than the PR title suggests — land the Sentry guard cleanly, then tighten a few footguns in docs/ops.

## Scope / PR hygiene

1. **Split or rename for clarity**  
   Title/branch say “disable sentry dev”, but half the diff is a full rewrite of `docs/operations/deployment.md` (profiles → always-on prod services, day-2 `-f` discipline). Prefer either:
   - two PRs (Sentry + tests first; runbook second), or
   - a title/body that names both (“Sentry opt-in in dev/test + prod start runbook”).

2. **Fill the empty PR body**  
   Call out the behavior change vs old `sentry_enabled()`: previously `APP_ENV=test` with a DSN alone would initialize Sentry; now it will not. That matters for anyone who copied a DSN into local/`tests` env files.

## Sentry correctness

3. **Document (or add) a staging/prod kill switch**  
   After this PR, `SENTRY_ENABLED=false` is a no-op whenever `APP_ENV` is `staging`/`production` and `SERVER_SENTRY_DSN` is set. That matches the docstring, but operators may assume the flag still disables shipping. Options:
   - keep current semantics and put a one-line warning in `.env.example` + configuration docs (“ignored outside development/test; clear the DSN to disable”), or
   - honor `SENTRY_ENABLED=false` as an emergency override in all envs (DSN + enabled).

4. **Mirror Sentry into `.env.production.example`**  
   The prod template still has no `SERVER_SENTRY_DSN` / `SERVER_SENTRY_RELEASE` / `SENTRY_ENABLED` (and is generally thinner than `.env.example`). Since the deployment doc tells people to copy that file, add the Sentry block there with the prod rule: DSN set ⇒ on; leave DSN blank to stay off.

5. **Tighten the test matrix a little**  
   Nice coverage already. Two cheap extras would lock the contract:
   - `SENTRY_ENABLED=true` + empty DSN → still `False` (DSN gate wins).
   - unknown/`prod` typo `APP_ENV` with DSN set → document expected behavior (today: treated as non-dev/test ⇒ on). If that is intentional, assert it; if not, validate `APP_ENV` against an allow-list.

6. **Client side is docs-only — say so**  
   `client/src/constants/sentry.ts` already opt-in on Vite `DEV`; this PR only sets `VITE_SENTRY_ENABLED=false` in `client/.env.development` and comments `.env.example`. Fine, but the PR body should note “no client logic change” so reviewers do not hunt for a TS diff.

## Deployment runbook

7. **Day-2 commands omit the cache overlay that `make prod` uses**  
   Section 3’s equivalent includes `-f docker-compose.cache.yml`, but section 6 (`logs` / `down` / `exec`) and the Celery DLQ samples use only `-f docker-compose.prod.yml`. That can leave `redis-cache` unmanaged or confuse project name/state. Prefer one documented compose invocation, e.g. a Make variable:

   ```makefile
   COMPOSE_PROD = docker compose -f docker-compose.prod.yml -f docker-compose.cache.yml
   prod-logs:
   	$(COMPOSE_PROD) logs -f
   prod-down:
   	$(COMPOSE_PROD) down
   ```

   …and point the runbook at those targets instead of repeating fragile `-f` lists.

8. **`make logs` / `make down` footgun**  
   Calling out that bare Make targets miss prod compose is good. Going further: either add `prod-logs`/`prod-down` (above) or make `logs`/`down` refuse to run when a prod project is detected, so the doc warning is not the only safety net.

9. **Todobot always-on crash-loop**  
   The note to set `TELEGRAM_BOT_TO_DO_TOKEN` is necessary. Stronger options if this bites in real deploys:
   - Compose `profiles: [bot]` on `todobot` even in prod, or
   - start the bot only when the token is non-empty (entrypoint guard) so a blank token does not restart forever.

10. **Optional search/Elasticsearch row dropped**  
    Old “Optional compose profiles” mentioned a search overlay; the new table keeps Postgres / AI search / Cloudflare but not Elasticsearch. If prod search is still a supported path, restore one row pointing at `docker-compose.search.yml` + `ELASTICSEARCH_URL`; if AI-only is the supported prod path, say that explicitly so the omission is intentional.

## Docs / config consistency

11. **Configuration table wording**  
    `docs/reference/configuration.md` already explains opt-in vs DSN-gated. Add a short “Disable in staging/prod” line (clear DSN / omit from process env) next to `SENTRY_ENABLED` so the ignored-flag case is not buried in prose.

12. **Sentry releases section vs runtime enablement**  
    The restored “Sentry releases (optional CI)” block covers sourcemap upload secrets but not runtime `SERVER_SENTRY_DSN` on the host. One sentence cross-link to configuration (and the new prod `.env` keys) would connect release upload to “events actually flow”.

## Test plan additions for #419

- [ ] With `APP_ENV=development`, DSN set, `SENTRY_ENABLED=false` → no Sentry init (API + Celery worker).
- [ ] Same with `SENTRY_ENABLED=true` → init once; no events from pytest unless explicitly opted in.
- [ ] Staging/production with DSN set and `SENTRY_ENABLED=false` → confirm intended behavior (on today).
- [ ] Vite DEV: default no client events; `VITE_SENTRY_ENABLED=true` + DSN sends a test error.
- [ ] Fresh host: copy `.env.production.example` → `make prod` → health/ready; day-2 logs/down use the same compose file set as start (including cache overlay).

## Suggested apply order

1. PR body + title/scope clarity (Sentry vs runbook).  
2. `.env.production.example` Sentry keys + kill-switch docs.  
3. One extra sentry unit case (enabled flag without DSN).  
4. `prod-logs` / `prod-down` (or fix day-2 `-f` lists to include cache).  
5. Optional follow-up: todobot guard / search row / APP_ENV allow-list.
