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

## Post-change snapshot (2026-10-30)

| Source | ~Tokens | Delta |
|--------|--------:|------:|
| `gortex-workflow.mdc` | 342 | −270 |
| `gortex-communities.mdc` | 84 | −466 |
| `project-context.mdc` | 374 | −31 |
| `agent-workflow.mdc` | 111 | 0 |
| `AGENTS.md` (full) | 530 | −488 |
| Skill catalog (all) | 146 | −799 |
| Skill catalog (`gortex-*`) | 0 | −799 |
| sessionStart inject | 25 | −121 |
| **Primary always-on sum** | **~1612** | **≈ −57% (−2175 tok/turn)** |

Estimate method: chars÷4 on always-on files + skill frontmatter catalog. Savings apply only to the controllable static slice, not total Cursor request cost.

## Flags / rollback

| Flag change | Status | How to roll back |
|-------------|--------|------------------|
| Offloaded `gortex-*` skills | **On**: `.cursor/references/gortex-skills/` (+ `.github/skills` mirrors removed) | Restore dirs to `.cursor/skills/` (and optionally `.github/skills/`) via git revert of move commits |
| Slim `gortex-workflow` / demoted communities | **On** | Revert `Slim Gortex always-on rules…` |
| Trimmed task-loop / personas | **On** | Revert `Shorten task-loop…` |

Discovery: Gortex `analyze(operation:"communities")`, [`.cursor/references/gortex-communities.md`](../../.cursor/references/gortex-communities.md), or Read under `.cursor/references/gortex-skills/`.

`.agents/skills` and `.claude/skills` symlink to `.cursor/skills` — lean catalog applies automatically.

Generator markers `<!-- gortex:communities:start -->` — re-sync from Gortex may reintroduce duplicate tables; keep pointers always-on and the full table only under `.cursor/references/`.

## Prompt / rule audit (keep · rewrite · delete · move)

| Item | Action | Reason |
|------|--------|--------|
| `project-context` purpose + stack | Keep | Product knowledge |
| `project-context` change bullets | Rewrite | Constraints, less overlap with agent-workflow |
| `AGENTS` dispatch table | Keep | High-value map |
| `AGENTS` / GEMINI / Copilot communities tables | Delete | Dup; discoverable via MCP/reference |
| Full communities table | Move | `.cursor/references/gortex-communities.md` |
| Gortex numbered steps | Rewrite | Plain tool descriptions |
| Gortex hard-stop when MCP missing | Rewrite | Soft fallback → Read/Grep |
| Worktree routing essay | Move | `.cursor/references/gortex-worktree-routing.md` |
| 27 `gortex-*` skill catalog entries | Move | Offload; rare first-turn need |
| sessionStart full git rules | Delete/move | Overlap with agent-workflow skill |
| `agent-workflow` stub → skill | Keep | Correct static/on-demand split |
| task-loop / manager / developer spawn text | Rewrite | Shorter constraints; point at workflow rule |

## Ranked changes (done)

| Rank | Layer | What | Est. savings | Quality risk | Validate | Rollback |
|------|-------|------|--------------|--------------|----------|----------|
| 1 | Tool/skill offload | Move `gortex-*` out of catalog | ~800 catalog tok/turn | Med | Community-area edit still finds code via MCP/refs | git mv back |
| 2 | Prompt dedupe | Drop communities from AGENTS/mirrors | ~500–1500 | Low | Dispatch table still works | revert dedupe commit |
| 3 | Prompt rewrite | Thin communities rule | ~450 | Low | Pointer still loads table on demand | revert |
| 4 | Prompt rewrite | Slim workflow + soft fallback | ~270 + fewer abort turns | Med | Gortex-down task completes | revert |
| 5 | Injected context | Slim sessionStart | ~120 | Low | Branch still injected | revert |
| 6 | Subagents | Trim task-loop/personas | Small per loop | Low | `/task-loop` smoke | revert |
| 7 | Groq | `stream_options.include_usage` | Cache telemetry | Low | Multi-turn chat logs cached_tokens | revert |
| 8 | Propose only | Cursor model mix / product cache | N/A in-repo | — | — | — |

## Test plan (flagged)

1. Simple Vue copy tweak — branch + coding standards still followed; no need for community skills.
2. FastAPI edit in a known community — find code via `analyze(communities)` or Read/Grep; no missing-skill errors.
3. Gortex MCP missing / `repo_not_tracked` — one report, then filesystem tools; no hard-stop.
4. `/task-loop` — Manager TASK yaml + Developer evidence; no extra coordination.
5. Admin AI chat 3-turn — `cached_tokens` present in logs on later turns when prefix is warm.

## Gaps

- No Cursor rendered-request, tool-schema tokens, cache hit rate, or price-weighted cost per coding task.
- Cannot set Cursor cache breakpoints or offload built-in Cursor tools.
- Cannot pass reasoning items for Cursor models.
- Model routing / reasoning-effort defaults: propose only (product-side).
