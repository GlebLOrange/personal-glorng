---
name: saving-workspace-context
description: Persist durable workspace knowledge (decisions, research, conventions) into the right project homes so it survives across chats.
user-invocable: false
---

# Saving Workspace Context

Build institutional memory. Prefer the project's existing homes; use `context/` only for leftovers.

## Modes

| Mode | When | What to do |
|------|------|------------|
| **Micro-save** | Skill in context / auto-attached mid-task | One short append to the correct home; mention the path; **no** full `context/` scan |
| **Full pass** | User invokes this skill or asks to persist session memory | Discover homes → selective load → save leftovers → end checklist |

Do **not** load the whole memory tree at the start of unrelated coding tasks.

## Memory Router (Before Any Write)

Route knowledge to the first matching home:

1. **Always-on constraints & conventions** → `.cursor/rules/` (**ask permission** first)
2. **Repeatable workflows** → new skill in `.cursor/skills/` or `~/.agents/skills/` (**ask permission** first)
3. **Bootstrap, environment, & agent setup** → `AGENTS.md`
4. **Architecture decisions** → `docs/adr/` (when ADR structure exists)
5. **Product & handbook docs** → existing `docs/` guides/specs
6. **Only then** → `context/{topic-slug}.md` for durable notes with nowhere else to live

If the project already documents truth in `AGENTS.md`, `docs/`, or `.cursor/rules/`, update or extend those — do not invent a parallel context tree.

## Full Pass: Selective Load

1. List known homes (`AGENTS.md`, `docs/`, `.cursor/rules/`, `context/`).
2. Read `context/README.md` or an index if present.
3. Open at most a few files whose names/topics match the current task.
4. Never dump the whole tree into the conversation context.

When first creating `context/`, add a short `context/README.md` agents can skim (one line per topic file).

## What to Save vs Skip

**Save:** decisions, non-obvious constraints, research synthesis, "where truth lives" maps, user preferences not already captured as rules.

**Don't save:** secrets, tokens, PII, `.env` contents, large logs or API dumps, anything easily re-derived from code, duplicates of existing AGENTS/docs/rules (update the real home instead).

**Write hygiene:**

- Append dated entries (newest first); don't overwrite history without reason.
- Mark superseded entries with `Superseded YYYY-MM-DD` instead of silent contradiction.
- Check for an existing slug before creating a new file.
- Use clear filenames so a directory listing is enough to find topics.

## Permission and Mention Rules

- **Micro-saves** to `context/` or one-line factual appends to docs: do without asking; **mention the file path**.
- **New skills or rules**: **ask permission** first.
- **Non-trivial edits** to `AGENTS.md` or tracked handbook docs: ask permission, or keep to a clean one-line append.

## End Checklist (Full Pass)

Before finishing a full pass:

- Are durable learnings captured in the right home?
- Is painful-to-redo research synthesized (not raw dumps)?
- Did a pattern emerge that should become a skill or rule? (ask before creating)
- Is there content that should be templated?

## File Formats

### `context/{slug}.md`

```markdown
# {Topic}

## {YYYY-MM-DD} — {Brief title}

{What was learned, decided, or discovered}

## {Earlier date} — {Earlier entry}

{Previous context}
```

### Project Stub (Only if no better home exists)

Prefer `AGENTS.md` / `docs/` when they exist. Otherwise a thin stub:

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
