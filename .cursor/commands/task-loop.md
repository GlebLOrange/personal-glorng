# Task loop (Manager → Developer → Reviewer)

You are the **parent Cursor control surface**. Orchestrate one controlled pass. Personas must not call each other — only you spawn them.

User request (after the command):

```text
$ARGUMENTS
```

If `$ARGUMENTS` is empty, ask once for the task text and stop.

## Rules

- Do **not** modify application code yourself. Delegate.
- Do **not** commit, push, open a PR, or merge unless the user later asks.
- **You (parent) create** the git branch `cursor/<slug>` before spawning Developer (never `agent/TASK-*`). Derive `<slug>` from Manager `branch_hint` or the user request.
- Gortex is a **tool**, not a persona. Do not spawn a Gortex agent.
- **QA is out of this loop.** Do not spawn `qa` here.
- At most **one** changes-requested retry, and only when the reviewer reports **Critical:** or required (no-prefix) findings. Then stop.

## Step 1 — Manager (Assign)

Spawn the `manager` subagent with:

```text
Mode: Assign (task-loop).

User request:
<paste $ARGUMENTS>

Do NOT modify files. Do NOT spawn personas. Do not write a task file.

1. Use Gortex (explore/task, search, relations as needed). On missing tools or repo_not_tracked: report once, use Read/Grep; do not invent graph results; do not run gortex track.
2. Emit exactly one TASK yaml in your reply that passes the requirement bar in .cursor/agents/README.md, then stop.
```

Wait for the TASK yaml. If Manager returns recommendations instead, ask once for Assign-mode yaml only. If still no TASK, stop and show the user what Manager returned.

## Step 2 — Branch (parent)

Create `cursor/<slug>` from Manager `branch_hint` (or a short kebab from the request) if not already on that branch. Do not leave Developer to create it during `/task-loop`.

## Step 3 — Developer

Spawn the `developer` subagent with **only** the TASK yaml plus:

```text
Implement this TASK from /task-loop.

- Work on the existing branch cursor/<slug> (parent already created it). Do not ask about the branch.
- Read CODING_STANDARDS.md before app edits. Stay inside scope; honor requirements and acceptance.
- Use Gortex before mutating when available. On missing tools or repo_not_tracked: report once, use Read/Grep/normal edits; do not invent graph results; do not run gortex track.
- Run only the checks listed under `checks:` in the TASK. If `checks` is empty, record SKIPPED (empty checks) — do not ask to run tests.
- Do NOT commit, push, open a PR, or merge.
- Return the developer evidence block (including requirement-bar one-liner).
```

Wait for the evidence report.

## Step 4 — Reviewer

Spawn the `code-reviewer` subagent with:

```text
Review this /task-loop handoff (readonly).

TASK yaml:
<paste TASK>

Developer evidence:
<paste developer report>

Inspect the branch diff (git diff against the base branch).
Judge TASK requirements AND acceptance (both). Use checks evidence as-is.
Verdict: APPROVE only if no Critical and no required findings; otherwise REQUEST CHANGES.
```

## Step 5 — Retry or stop

- If **APPROVE**: stop. Summarize branch, TASK id/goal, reviewer overview. Merge/commit is the user's.
- If **REQUEST CHANGES** with at least one **Critical:** or required (no-prefix) finding:
  1. Spawn `developer` once with TASK, prior evidence, and those Critical + required findings. Same constraints.
  2. Spawn `code-reviewer` once with updated evidence + diff.
  3. Stop. Do **not** retry again.
- If **REQUEST CHANGES** with only Nit / Optional / FYI: do **not** retry; stop with that verdict.

## Final message to the user

```text
## Task-loop result
- Branch: …
- Verdict: APPROVE | REQUEST CHANGES
- Requirement bar: …
- Changed: …
- Checks: …
- Next: you commit / open PR / merge when ready
```
