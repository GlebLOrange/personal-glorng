# Agent token baseline

Comparable estimates for **repo-controlled** Cursor always-on context. Not Cursor provider billing.

Measure: `python3 scripts/agent_token_baseline.py` (chars ÷ 4 ≈ tokens).

## Pre-change snapshot (2026-10-30)

| Source | ~Tokens | Note |
|--------|--------:|------|
| `gortex-workflow.mdc` | 612 | alwaysApply |
| `gortex-communities.mdc` | 550 | alwaysApply table |
| `project-context.mdc` | 405 | keep |
| `agent-workflow.mdc` | 111 | stub → skill |
| `AGENTS.md` (full) | 1018 | includes communities ~524 |
| Skill catalog (all) | 945 | |
| Skill catalog (`gortex-*`) | 799 | offload candidate |
| Skill catalog (product) | 146 | keep |
| sessionStart inject | 146 | volatile |
| **Primary always-on sum** | **~3787** | rules + AGENTS + catalog + hook |

Communities table also mirrored in `GEMINI.md` and `.github/copilot-instructions.md` (~524 each; host-specific, not always Cursor).

## Flags / rollback

| Flag change | How to roll back |
|-------------|------------------|
| Offloaded `gortex-*` skills | `git mv .cursor/references/gortex-skills/* .cursor/skills/` (or revert the move commit) |
| Slim `gortex-workflow` / demoted communities | Revert that commit |
| Trimmed task-loop / personas | Revert that commit |

Generator markers `<!-- gortex:communities:start -->` — re-sync from Gortex may reintroduce duplicate tables; keep a single always-on pointer and put the full table only under `.cursor/references/`.

## Gaps

- No Cursor rendered-request or cache-hit telemetry in-repo.
- Cannot set provider cache breakpoints or offload Cursor built-in tools from this repo.
