# Agent Personas

Custom agent definitions for this repository live in `.cursor/agents/`.

## Available personas

| Persona | File | Use when |
|---------|------|----------|
| Code reviewer | [`code-reviewer.mdc`](code-reviewer.mdc) | Thorough five-axis review before merge |
| Manager | [`manager.md`](manager.md) | Prioritize next portfolio work, or Assign a TASK yaml for `/task-loop` |
| Developer | [`developer.md`](developer.md) | Implement a scoped task on a `cursor/*` branch |
| QA | [`qa.md`](qa.md) | Inspect/test for bugs and regressions (readonly; links, nav, forms, console/API, responsive, tests) |
| Recruiter | [`recruiter.md`](recruiter.md) | Screen the site for Python/backend hiring signal |
| UX | [`ux.md`](ux.md) | Audit UI, usability, and accessibility (do not change app code) |

## Orchestration

**`/task-loop`** (`.cursor/commands/task-loop.md`) is the only orchestrator for the controlled loop:

```text
Manager (Assign TASK) → Developer (implement + evidence) → code-reviewer (APPROVE | REQUEST CHANGES)
```

- Parent Cursor chat runs the command and spawns personas in order.
- Personas **do not** invoke each other.
- Gortex is a shared **tool** (repository intelligence), not a persona.
- Git boundary: work on `cursor/<slug>`; human merges after approval.
- **QA is not in this loop yet.** After `/task-loop` is proven, QA can be inserted between Developer and Reviewer.

## Composition

- **Invoke directly** when the user asks for a review of a specific change, file, or PR.
- **Do not invoke from another persona.** If a persona wants specialized security or test coverage, surface that as a recommendation in the report — orchestration belongs to slash commands (`/task-loop`, `/review`, `/ship`), not nested persona calls.

## Severity labels

| Prefix | Meaning |
|--------|---------|
| **Critical:** | Blocks merge |
| *(no prefix)* | Required — must fix before merge |
| **Nit:** | Minor, optional |
| **Optional:** / **Consider:** | Suggestion |
| **FYI** | Informational only |
