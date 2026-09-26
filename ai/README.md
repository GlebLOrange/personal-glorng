# Autonomous development harness (DSH + Cursor + Gortex)

This directory is **not** part of the Gleb.Y runtime (`server/`, `client/`). It holds shared context, task contracts, and workflow definitions for agents that **develop** the portfolio.

## Separation of concerns

| Layer | Role |
|-------|------|
| **Cursor** | Human UI, edits, PR review, Cloud Agents |
| **DeepSeek Harness (DSH)** | External orchestration runtime (sessions, agent loop, model adapter) |
| **Gortex MCP** | Repository code graph (search, impact, edit, tests) — see `.cursor/rules/gortex-workflow.mdc` |
| **`server/` AI features** | Product features for site users (`ai_chat`, `task_intake`) — unrelated to this harness |

## Target flow

```
You → Cursor → Manager → Developer → Reviewer (+ QA when needed)
                      ↘ Gortex MCP ↙
                      personal-glorng (git branch, tests)
```

Guardrails (non-negotiable for experiments):

- No automatic merge to `main`
- No production credentials in harness config
- No unrestricted filesystem access outside the repo checkout
- Branch prefix `cursor/` (or future `agent/`) — never commit directly on `main`

## Layout

```
ai/
├── README.md           ← you are here
├── context/            ← stable project contract (DSH system prompts cite these)
├── agents/             ← DSH-oriented agent briefs (mirror .cursor/agents where useful)
├── workflows/          ← step graphs (Manager → Developer → Reviewer)
└── tasks/              ← task YAML instances (e.g. TASK-001)
```

**Source of truth:** Cursor rules and skills under `.cursor/` remain authoritative for day-to-day coding. Files in `ai/context/` summarize and point to them so DSH does not fork policy.

## Phases

1. **Scaffold** — `ai/` + `developer` Cursor persona (this repo state).
2. **DSH beside repo** — run harness externally; DeepSeek API via env; no app changes.
3. **Gortex in DSH** — same MCP config as `.cursor/mcp.json` (adjust paths per machine).
4. **Pilot workflow** — one small change, no public API change; tests + human PR.
5. **Autonomy** — loops, persistence, optional `agent/*` branches (after pilot is boring).

## DSH runtime location

Do not vendor DSH inside `server/` or `client/`. Clone/run DSH as a sibling directory or pinned version elsewhere; point it at this repo root and load prompts from `ai/`.

## First experiment (template)

See [`workflows/small-improvement.md`](workflows/small-improvement.md) and [`tasks/TASK-001.example.yaml`](tasks/TASK-001.example.yaml).
