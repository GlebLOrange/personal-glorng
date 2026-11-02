# Task loop (Manager → Developer)

Parent Cursor control surface: one controlled pass. Only you spawn personas.

```text
$ARGUMENTS
```

If empty, ask once for the task text and stop.

## Constraints

- Do not modify application code; delegate. No commit/push/PR/merge unless the user later asks.
- Create `cursor/<slug>` before Developer (never `agent/TASK-*`); slug from Manager `branch_hint` or the request.
- Do not spawn Gortex, `qa`, or `code-reviewer`. Stop after Developer.

## 1 — Manager (Assign)

Spawn `manager` with:

```text
Mode: Assign (task-loop).
User request:
<paste $ARGUMENTS>

Do not modify files, spawn personas, or write a task file.
Use Gortex per .cursor/rules/gortex-workflow.mdc.
Emit exactly one TASK yaml that passes .cursor/agents/README.md requirement bar, then stop.
```

Wait for TASK yaml. If recommendations instead, ask once for Assign-mode yaml only; else stop and show what Manager returned.

## 2 — Branch

Create `cursor/<slug>` from `branch_hint` (or short kebab) if not already on it.

## 3 — Developer

Spawn `developer` with the TASK yaml plus:

```text
Implement this TASK from /task-loop.
- Stay on existing branch cursor/<slug>; do not ask about the branch.
- Read CODING_STANDARDS.md before app edits; stay in scope.
- Gortex: .cursor/rules/gortex-workflow.mdc.
- Run only TASK `checks:`; empty checks → SKIPPED (empty checks).
- Do not commit, push, or open a PR.
- Return the developer evidence block (requirement-bar one-liner included).
```

Wait for evidence, then stop.

## Final message

```text
## Task-loop result
- Branch: …
- TASK: …
- Requirement bar: …
- Changed: …
- Checks: …
- Next: you commit / open PR / merge when ready
```
