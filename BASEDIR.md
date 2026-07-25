# PR #421 improvement suggestions

Review target: [chore(dev-env): fix cloud-vm overlay for mongodb/rabbitmq + document setup caveats](https://github.com/GlebLOrange/personal-glorng/pull/421) (`cursor/dev-env-setup-f152` → `main`).

Verdict: ship it. The `mongodb` / `rabbitmq` overlay fix is the real unblocker, and the AGENTS.md caveats match what Cloud Agents hit. Treat the items below as small follow-ups — none should block this thin env/docs PR.

## High-value follow-ups

1. **Add `elasticsearch` to `docker-compose.cloud-vm.yml`**  
   Base compose gives ES `deploy.resources.limits.memory: 768M`. AGENTS.md tells agents to use the cloud overlay with `make dev-search` / `--profile search`, but the overlay still omits `elasticsearch`, so search mode will hit the same `cgroupv2 … threaded mode` crash mongodb/rabbitmq just escaped. Mirror the other limited services:

   ```yaml
   elasticsearch:
     cgroup: host
     deploy: !reset null
   ```

2. **Fix the root cause of the SEED_PASSWORD trap in `.env.example`**  
   Documenting the gotcha is good; leaving `SEED_PASSWORD=password_seed` (and `E2E_PASSWORD=password_seed`) still burns the next agent. Prefer:

   - set both to a policy-compliant value that matches the documented E2E creds (`MyTestPass123!`), and  
   - tighten seed validation to call `validate_password_strength` (today `WEAK_PASSWORDS` only blocks a tiny deny-list, so `password_seed` still seeds successfully and fails only at login).

3. **Wire the cloud overlay into Make (stop claiming equivalence)**  
   AGENTS.md says the long compose command is “equivalent to `make dev-lite`”, but `make dev-lite` / `dev-search` / `dev-ultra-lite-infra` never pass `-f docker-compose.cloud-vm.yml`, and step 2 still tells agents to run `make dev-lite`. On this VM that fails. Options (pick one):

   - `COMPOSE_CLOUD ?= -f docker-compose.cloud-vm.yml` toggled by `CLOUD_VM=1` or auto-detect nested Docker, or  
   - explicit targets: `dev-lite-cloud`, `dev-search-cloud`, `dev-ultra-lite-infra-cloud`.

   Then point AGENTS.md at the Make target instead of a hand-copied compose line.

4. **Guard against the next missing overlay service**  
   The mongodb/rabbitmq miss happened because the overlay is a hand-maintained allowlist. Add a tiny check (CI or `scripts/check_cloud_vm_overlay.sh`) that every service in `docker-compose.yml` with `deploy.resources` also appears in `docker-compose.cloud-vm.yml` with `deploy: !reset null`. Cheap insurance.

## Docs / DX polish

5. **Align the documented `up` service list with reality**  
   Example command starts `mongodb redis server` but lite also needs `redis-cache` (and pulls `rabbitmq` / `migrate` via `depends_on`). Prefer the same set as Makefile: `mongodb redis redis-cache server` (plus `nginx` if matching `dev-lite`), or say “compose will start depends_on” explicitly so agents do not wonder why extra containers appear.

6. **Break the Docker caveat wall of text into bullets**  
   The Docker 29 / `fuse-overlayfs` / overlay-must-cover-every-limited-service paragraph is accurate but hard to scan. Split into short bullets: daemon.json requirements, per-session `dockerd`, overlay completeness rule, failure signature to search for.

7. **Optional: one bootstrap script for daemon.json + dockerd**  
   Agents can mis-edit `/etc/docker/daemon.json` (especially the Docker 29 `containerd-snapshotter: false` bit). A `scripts/cloud-vm-docker.sh` that writes the known-good daemon config, restarts/starts `dockerd`, and waits on `docker info` would make the AGENTS.md prose operational instead of copy-paste fragile.

8. **Keep known-broken frontend CI out of permanent AGENTS.md status**  
   The `npm ci --legacy-peer-deps` / TS7 vs `typescript-eslint` notes are useful *right now*, but they duplicate what should be a tracked issue/PR. After the dep fix lands, delete those bullets so AGENTS.md stays an env bootstrap, not a CI status board. Link an issue if you keep them temporarily.

9. **Seed password update path**  
   Docs correctly say `seed_admin` skips existing users and you need `down -v`. A small escape hatch (`SEED_PASSWORD_FORCE=1` or “update password when email matches seed admin”) would avoid volume wipes when someone already seeded with `password_seed`.

## Nice-to-have consistency checks before merge (optional)

10. **Confirm overlay coverage matrix** (manual or script):

    | Service with `deploy.resources` | In cloud-vm overlay? |
    |---|---|
    | `db` | yes |
    | `mongodb` | yes (this PR) |
    | `rabbitmq` | yes (this PR) |
    | `redis` | yes |
    | `redis-cache` | yes |
    | `elasticsearch` | **no — follow-up #1** |

11. **Smoke after follow-ups**  
    - `… -f docker-compose.cloud-vm.yml --profile search up elasticsearch` stays healthy.  
    - Fresh `.env` from `.env.example` → `make seed` → login with the documented E2E password works without editing SEED_PASSWORD.  
    - `make dev-lite-cloud` (or `CLOUD_VM=1 make dev-lite`) starts the lite stack without a hand-rolled compose line.

## Suggested apply order

1. Merge #421 as-is (overlay fix + docs unblock Cloud Agents today).  
2. Tiny follow-up: add `elasticsearch` to the overlay (+ optional overlay completeness check).  
3. `.env.example` / seed policy alignment so SEED_PASSWORD cannot recreate the login trap.  
4. Make target / `CLOUD_VM` wiring so AGENTS.md can stop duplicating compose flags.
