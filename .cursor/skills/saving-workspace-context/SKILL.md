---
name: saving-workspace-context
description: >-
  Persists durable decisions, research, and conventions into existing project homes
  (AGENTS.md, docs/, .cursor/). Use when asked to save workspace context, persist
  decisions, or carry conventions across chats.
user-invocable: true
---

# Saving Workspace Context

Build institutional memory. Prefer the project's existing homes (`AGENTS.md`, `CODING_STANDARDS.md`, `docs/`, `.cursor/rules/`, `.cursor/skills/`).

## Modes

| Mode | When | What to do |
|------|------|------------|
| **Micro-save** | Gated stop hook (see below), or skill in context mid-task | One short dated append to the correct home; mention the path. If nothing durable, edit nothing and reply exactly: `No workspace context to save.` |
| **Full pass** | User asks to persist session memory (slash / attach this skill) | Discover homes → selective load → save → end checklist |

Do **not** load the whole memory tree at the start of unrelated coding tasks.

## Stop hook (auto micro-save)

Cursor’s `stop` payload is only `{ status, loop_count }` — no transcript or file list. Blind every-turn follow-ups are mostly noise.

This repo gates micro-save:

1. [`session-start.sh`](../../hooks/session-start.sh) exports `PORTFOLIO_CTX_SESSION` from `session_id`.
2. [`after-file-edit-mark.sh`](../../hooks/after-file-edit-mark.sh) marks the session dirty after any agent file edit (temp state under `$TMPDIR/portfolio-glorng-ctx/`).
3. [`save-workspace-context.sh`](../../hooks/save-workspace-context.sh) emits a follow-up only when `status == completed`, `loop_count == 0`, the session is dirty, and it has not already been prompted. Then it marks `prompted` so later stops stay silent.

Wired in [`.cursor/hooks.json`](../../hooks.json) (`afterFileEdit` + `stop` with `loop_limit: 1`). Empty `{}` from the stop script means no chat follow-up.

Ask / Plan turns with no edits never trigger micro-save. When a follow-up does fire and nothing is durable, **`No workspace context to save.`** is still the correct reply.

Prefer this project skill over a global `~/.agents/skills/Saving-Workspace-Context/SKILL.md` copy (different router). `user-invocable: true` so slash / attach uses this file.

## How to update this later

- Policy (what to save, router, full-pass steps): this `SKILL.md`
- Gate / empty reply / follow-up text: [`.cursor/hooks/save-workspace-context.sh`](../../hooks/save-workspace-context.sh), [`.cursor/hooks/after-file-edit-mark.sh`](../../hooks/after-file-edit-mark.sh), [`.cursor/hooks/session-start.sh`](../../hooks/session-start.sh), [`.cursor/hooks.json`](../../hooks.json)
- Worktree checkouts only see hook edits after that commit lands on their branch

## Memory Router (Before Any Write)

Route knowledge to the first matching home:

1. **Always-on constraints & conventions** → `.cursor/rules/` (**ask permission** first)
2. **Repeatable workflows** → new skill in `.cursor/skills/` or `~/.agents/skills/` (**ask permission** first)
3. **Agent entry map (dispatch only)** → `AGENTS.md`
4. **Which skill to open / coding standards index** → `CODING_STANDARDS.md`
5. **Setup, ports, seed** → `docs/guide/getting-started.md`, `README.md`
6. **Cloud VM Docker** → `docs/operations/cloud-vm.md`
7. **Persona / requirement bar** → `.cursor/agents/README.md`
8. **Architecture decisions** → `docs/adr/` (when ADR structure exists)
9. **Product & handbook docs** → existing `docs/` guides/specs

If the project already documents truth in those homes, update or extend them — do not invent a parallel dump tree.

## Full Pass: Selective Load

1. List known homes (`AGENTS.md`, `CODING_STANDARDS.md`, `docs/`, `.cursor/rules/`, `.cursor/skills/`, `.cursor/agents/`).
2. Open at most a few files whose names/topics match the current task.
3. Never dump the whole tree into the conversation context.

## What to Save vs Skip

**Save:** decisions, non-obvious constraints, research synthesis, "where truth lives" maps, user preferences not already captured as rules.

**Don't save:** secrets, tokens, PII, `.env` contents, large logs or API dumps, anything easily re-derived from code, duplicates of existing AGENTS/docs/rules (update the real home instead).

**Write hygiene:**

- Append dated entries (newest first); don't overwrite history without reason.
- Mark superseded entries with `Superseded YYYY-MM-DD` instead of silent contradiction.
- Prefer updating an existing doc over creating a new file.

## Permission and Mention Rules

- **One-line factual appends** to docs: do without asking; **mention the file path**.
- **New skills or rules**: **ask permission** first.
- **Non-trivial edits** to `AGENTS.md` or tracked handbook docs: ask permission, or keep to a clean one-line append.

## End Checklist (Full Pass)

Before finishing a full pass:

- Are durable learnings captured in the right home?
- Is painful-to-redo research synthesized (not raw dumps)?
- Did a pattern emerge that should become a skill or rule? (ask before creating)
- Is there content that should be templated?

## Project Stub (Only if no better home exists)

Prefer `AGENTS.md` / `CODING_STANDARDS.md` / `docs/` when they exist. Otherwise a thin stub in docs:

```markdown
# {Project Name} — Context

- **What it is:** {one line}
- **Who it's for:** {audience}
- **Current goals:** {what matters now}

## Where truth lives

- Agents / bootstrap: `{path}`
- Docs / ADRs: `{path}`
- Rules: `{path}`

## Constraints

{Things to always keep in mind}
```
