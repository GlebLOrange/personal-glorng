# Workflow: small improvement (pilot)

Manager → Developer → Reviewer, optional QA if user-facing.

## 1. Manager

**Input:** Natural language goal (e.g. “find one small technical improvement without public API change”).

**Actions:**

- Inspect repo (Gortex explore or readonly search).
- Emit one task file under `ai/tasks/` from [`../tasks/TASK-001.example.yaml`](../tasks/TASK-001.example.yaml).
- Set `specialist: developer`, explicit acceptance criteria, and `public_api_change: false`.

**Output:** Task ID + branch name suggestion (`cursor/<slug>`).

## 2. Developer

**Input:** Task YAML + `ai/context/*` + relevant `.cursor/skills/*`.

**Actions:**

- Create branch; implement minimal diff.
- Run targeted tests (see backend.md / frontend.md).
- Push branch; open **draft** PR (human merges).

**Output:** PR link, test command output summary, files touched.

## 3. Reviewer

**Input:** Task YAML + git diff + test summary only (no full repo re-scan unless needed).

**Actions:**

- Apply `.cursor/agents/code-reviewer.mdc` five-axis review.
- Verdict: **PASS** (ready for human merge) or **FAIL** (return to Developer with numbered fixes).

## 4. QA (optional)

Invoke when change touches navigation, forms, auth, or visible UX. Use `.cursor/agents/qa.md` (readonly).

## Failure loop

Reviewer **FAIL** → Developer (max 2 iterations in pilot) → escalate to human.
