# PR #423 improvement suggestions

Review target: [Add BASEDIR.md with PR #422 CI improvement suggestions](https://github.com/GlebLOrange/personal-glorng/pull/423) (`cursor/basedir-file-improvements-581c` → `main`).

Verdict: useful capture of #422 follow-ups, but the notes are already partly stale against #422 tip `a872646`, underspecify current red checks, and would land ephemeral review noise on `main` without a freshness contract. Refresh or reshape before merge.

## Blockers / must-fix before merging #423 as-is

1. **Refresh against current #422 tip (`a872646`)**  
   Several “blockers” in the current `BASEDIR.md` are outdated:
   - **Done:** `GITHUB_TOKEN` for `gitleaks-action@v3` — gitleaks is green.
   - **Changed:** `npm_audit` no longer runs `npm ci`; it uses `npm audit --package-lock-only`. Peer conflict is no longer the audit failure mode.
   - **Was red on #422 tip; frontend peer conflict fixed later (#427):** TypeScript is pinned to `~5.8.3`; plain `npm ci` works. Remaining historical notes for that tip: backend (Ruff format + lint), docs (stale `docs/generated`), postgres-tests (`ImportError: normalize_feed_articles` from `app.services.news`), npm_audit (real high: `brace-expansion` GHSA-3jxr-9vmj-r5cp / GHSA-mh99-v99m-4gvg).  
   Rewrite the blocker list to match tip SHA + check conclusions, or readers will chase fixed work.

2. **Add the missing postgres collection failure**  
   Current notes omit `postgres-tests` failing during collection:

   ```text
   ImportError: cannot import name 'normalize_feed_articles' from 'app.services.news'
   ```

   That is a real gate failure once `ci-ok` + path filters select postgres (this PR touches workflows → postgres=true). Call it out as a #422 unblock item (delete/update the stale import in `server/tests/test_news.py`, or restore the helper).

3. **Correct the Ruff diagnosis**  
   “5 Ruff errors” understates tip reality: `ruff format --check` wants **16 files** reformatted, plus lint hits (`ANN401` in `app/db/mongo/client.py`, `I001` in `app/routers/auth.py`, …). Prefer: run `uv run ruff format` + `uv run ruff check --fix` on the #422 branch (or a tiny preceding hygiene PR) and paste the remaining non-auto-fixable codes.

4. **Mark npm_audit as a real advisory, not a peer install flake**  
   Lockfile-only audit exits 1 on high `brace-expansion`. Suggestion should be `npm audit fix` / bump transitive deps in `client/package-lock.json` (or temporarily raise audit level with a tracked follow-up).

## Doc / process hygiene for #423

5. **Do not merge stale review notes onto `main` without a freshness header**  
   At minimum add at the top:

   ```md
   Reviewed PR: #422 @ <full SHA>
   Checks snapshot: <UTC timestamp>
   Status: living notes — update or delete after #422 merges
   ```

   Better: keep this as a PR comment / automation artifact and **do not commit** `BASEDIR.md` to `main`, or put it under `docs/operations/` / `.cursor/` with an explicit “ephemeral” note in `.gitignore` if the file is only for agent handoff.

6. **Rename or relocate if this stays in-repo**  
   `BASEDIR.md` at repo root reads like project layout docs, not “latest automation review”. Prefer something explicit (`docs/operations/pr-422-ci-followups.md` or `.cursor/reviews/pr-422.md`) so humans and agents do not treat it as canonical architecture.

7. **Add a done/open checklist keyed to check names**  
   Mirror the GitHub check names the ruleset will require (`ci-ok`, `gitleaks`, plus non-required but selected jobs). Example:

   | Check | #422 tip | Action |
   | --- | --- | --- |
   | gitleaks | pass | none |
   | pip_audit | pass | none |
   | npm_audit | fail | bump `brace-expansion` |
   | frontend | fail | TS ↔ eslint peer align |
   | backend | fail | ruff format/lint |
   | postgres-tests | fail | fix `normalize_feed_articles` import |
   | docs | fail | `make docs-generate` |
   | ci-ok | fail | turns green after above |

8. **Call out that #423 itself proves the all-skip green risk**  
   This PR only adds `BASEDIR.md`. Path filters select nothing → every suite skipped → `ci-ok` can still succeed. That is the strongest concrete example for the “catch-all / no-match fallback” suggestion already in the notes — promote it with this evidence instead of a hypothetical README-only PR.

## Gate suggestions that remain valid (keep, but re-home)

These #422 items in the current file are still right; keep them after the refresh:

9. **Fail `ci-ok` when `changes` fails** — today empty outputs look like skips under `if: always()`.
10. **No-match fallback** — if no filter matches, run a cheap smoke (backend and/or frontend), not an empty green gate.
11. **Widen/collapse filters** — `shared/**`, compose, `.env.example`; collapse duplicate postgres≡backend path lists.
12. **Relax backend `timeout-minutes: 7`** until p95 timings exist.
13. **Prefer a thin CI-only PR** to unblock #419/#420; keep lite-default Make/env/Sentry-disable as follow-up.

## Test plan additions for #423

- [ ] Re-pull #422 checks at tip SHA and rewrite blockers to match (gitleaks/pip_audit green; list current reds).
- [ ] Include postgres `normalize_feed_articles` ImportError and npm high advisory by name.
- [ ] Decide merge destiny: ephemeral path vs `docs/operations/` with freshness header — do not leave an undated root `BASEDIR.md` on `main`.
- [ ] Explicitly document that a `BASEDIR.md`-only PR skips all suites under current filters.

## Suggested apply order for #423

1. Refresh content against #422 `@a872646` (or newer tip).  
2. Add freshness header + done/open check table.  
3. Relocate/rename or mark ephemeral so `main` does not accumulate stale agent notes.  
4. Keep the still-valid gate/filter follow-ups; drop fixed gitleaks-token / peer-based npm_audit guidance.
