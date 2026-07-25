# PR #422 improvement suggestions

Review target: [CI: add ci-ok gate and fix gitleaks/security workflow](https://github.com/GlebLOrange/personal-glorng/pull/422) (`cursor/ci-workflows-tune` → `main`).

Verdict: direction is right (`ci-ok` aggregator + path filters + gitleaks restore), but the PR does not currently go green and a few gate edge cases will bite once `main-protection` is enforced. Fix blockers first, then the small correctness/scope items below.

## Blockers (CI red on the PR)

1. **Pass `GITHUB_TOKEN` to gitleaks-action@v3**  
   Current failure: `GITHUB_TOKEN is now required to scan pull requests`.  
   In `.github/workflows/security.yml` under the Scan for secrets step:

   ```yaml
   env:
     GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
     GITLEAKS_ENABLE_UPLOAD_ARTIFACT: "false"
   ```

2. **Frontend / npm_audit `npm ci` peer conflict**  
   `typescript@7.0.2` vs `typescript-eslint@8.65.0` peer `typescript@">=4.8.4 <6.1.0"`.  
   Path filters force frontend + npm_audit because this PR touches `ci.yml` / `security.yml`, so a pre-existing client peer mismatch now fails the merge gate path. Either:
   - align eslint stack to TS 7 (or pin TS back to supported range), or
   - temporarily use `npm ci --legacy-peer-deps` in CI/audit **only** with a tracked follow-up.

3. **Backend Ruff failures**  
   Backend job reports 5 Ruff errors (some auto-fixable). Clean those on the PR branch (or confirm they are pre-existing on `main` and fix in a tiny preceding PR so `ci-ok` is honest).

4. **Docs job: stale `docs/generated`**  
   Run `make docs-generate` and commit, or drop `server/app/**` from the docs filter if this PR should not require a docs regen.

## Gate correctness

5. **Fail `ci-ok` when `changes` fails**  
   Today `ci-ok` uses `if: always()` and treats empty selection outputs as “skipped”, so a failed `changes` job can still yield a green aggregator. Add an early hard fail:

   ```bash
   if [ "${{ needs.changes.result }}" != "success" ]; then
     echo "changes job failed"
     exit 1
   fi
   ```

6. **Avoid all-skip green merges for risky root files**  
   PRs that only touch `README.md`, `AGENTS.md`, `.env.example`, `shared/**`, `scripts/**` (non-docs), `deploy/**`, etc. currently skip every suite and still pass `ci-ok`. Prefer either:
   - a catch-all `core` filter that forces backend (or a cheap smoke job), or
   - “if no filter matched → run backend + frontend” fallback in the Select jobs step.

7. **Widen filters that are too narrow for this repo**  
   - backend: also `shared/**`, `Makefile` targets that affect server, relevant compose files, `.env.example` when settings contract changes.  
   - e2e: already broad; keep forcing frontend when e2e is selected (good).  
   - postgres: identical to backend today — collapse to one output or `needs: backend` to avoid duplicate path lists.

8. **Timeouts may be tight**  
   Backend `timeout-minutes: 7` with parallel Ruff/Mypy + pytest+cov is aggressive on cold cache. Prefer 10–12 until you have p95 job timings from a few green runs.

## Security workflow

9. **Add a `security-ok` aggregator (optional but consistent)**  
   Ruleset only requires `gitleaks`, so skipped/failed `pip_audit` / `npm_audit` are easy to miss in the UI. A small aggregator (same pattern as `ci-ok`) makes the workflow status obvious without changing the ruleset yet.

10. **Pin / document gitleaks version behavior**  
    Action installs its own binary (`8.24.3` observed). Fine for now; if scans become noisy or flaky, pin `GITLEAKS_VERSION` explicitly so upgrades are intentional.

11. **npm audit install vs audit-only**  
    Full `npm ci` is heavy (and currently broken on peers). Prefer `npm audit --omit=dev` against the lockfile where possible, or `npm ci --ignore-scripts` once peers are fixed, to keep the security job cheap.

## Scope / product hygiene on the same PR

12. **Split unrelated changes if you want a minimal unblock PR**  
    The CI gate fix is mixed with: lite-as-default Make/compose, `.env.example` Celery/logging defaults, middleware health-path skip, skills `.gitignore`, Sentry workflow hard-disable, docs churn. A thin PR that only lands `ci.yml` + `security.yml` (+ checklist note) unblocks `#419`/`#420` faster; follow with the lite-default stack PR.

13. **Document existing-clone migration for env defaults**  
    Changing `.env.example` to `CELERY_TASK_ALWAYS_EAGER=true` / `LOG_REQUESTS=false` does not update existing `.env` files. One short note in `docs/guide/development.md` (“re-copy or set these two keys”) avoids surprise broker dependency in local lite.

14. **Sentry workflow `if: false`**  
    Hard-disable is clear for development. Prefer keeping the tag trigger in comments as a copy-paste block (already partly done) and linking the devops checklist row so restore is one checklist item, not archaeology.

## Test plan additions for #422

- [ ] Confirm gitleaks job is green with explicit `GITHUB_TOKEN`.
- [ ] Confirm `ci-ok` fails when any selected job fails **and** when `changes` fails.
- [ ] Open a README-only draft PR and decide whether all-skip → green is acceptable once the ruleset is Active.
- [ ] After merge, record the exact check names shown in the PR UI before enabling `main-protection`.

## Suggested apply order

1. `GITHUB_TOKEN` for gitleaks (unblocks required check).  
2. Frontend peer / Ruff / docs-generated so `ci-ok` can go green.  
3. `ci-ok` fail-on-`changes` + filter fallback.  
4. Optionally split lite-default / logging / Sentry disable into a follow-up.
