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
- Git branch prefix is **`cursor/<slug>`** only (never `agent/TASK-*`).
- Gortex is a **tool** for agents, not a persona. Do not spawn a Gortex agent.
- **QA is out of this loop.** Do not spawn `qa` here.
- At most **one** changes-requested retry (developer fix → reviewer re-check), then stop.

## Step 1 — Manager (Assign)

Spawn the `manager` subagent with this prompt:

```text
Mode: Assign (task-loop).

User request:
<paste $ARGUMENTS>

Do NOT modify files.

1. Use Gortex (explore/task, search, relations as needed) to find scope.
2. Emit exactly one TASK yaml contract (see manager Assign mode), then stop.
```

Wait for the TASK yaml. If Manager returns recommendations instead of a single TASK, ask Manager once to emit Assign-mode yaml only. If still no TASK, stop and show the user what Manager returned.

## Step 2 — Developer

Spawn the `developer` subagent with **only** the TASK yaml (plus this instruction):

```text
Implement this TASK from /task-loop.

- Follow agent-git-workflow: work on cursor/<slug> (create if on main after asking once).
- Use Gortex before mutating (impact; verify if signatures change).
- Run only the checks listed under `checks:` in the TASK (that counts as the user asking for those checks).
- Do NOT commit, push, open a PR, or merge.
- Return the evidence handoff block required by developer.md.
```

Wait for the evidence report (changed files, check results, `git diff --stat`).

## Step 3 — Reviewer

Spawn the `code-reviewer` subagent with:

```text
Review this /task-loop handoff.

TASK yaml:
<paste TASK>

Developer evidence:
<paste developer report>

Inspect the branch diff (git diff against the base branch). Review against the TASK acceptance criteria.
Verdict must be APPROVE or REQUEST CHANGES.
```

## Step 4 — Retry or stop

- If **APPROVE**: stop. Summarize for the user: branch name, TASK id/goal, reviewer overview. Tell them merge/commit is theirs.
- If **REQUEST CHANGES**:
  1. Spawn `developer` once with the TASK, prior evidence, and the reviewer’s required findings. Same constraints (checks in TASK, no commit/PR/merge).
  2. Spawn `code-reviewer` once with updated evidence + diff.
  3. Stop with the final verdict. Do **not** retry again.

## Final message to the user

Always end with:

```text
## Task-loop result
- Branch: …
- Verdict: APPROVE | REQUEST CHANGES
- Changed: … (from developer evidence)
- Checks: … (from developer evidence)
- Next: you commit / open PR / merge when ready
```
