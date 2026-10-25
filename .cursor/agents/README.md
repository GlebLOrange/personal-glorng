# Agent Personas

Definitions live in `.cursor/agents/`. Shared rules live **here** (and Gortex fallback in `.cursor/rules/gortex-workflow.mdc`) — not duplicated inside personas.

## Available personas

| Persona | File | Use when |
|---------|------|----------|
| Manager | [`manager.md`](manager.md) | Recommend work, or Assign one TASK yaml for `/task-loop` (does not spawn) |
| Developer | [`developer.md`](developer.md) | Implement on `cursor/*` (only mutating persona) |
| QA | [`qa.md`](qa.md) | Readonly defects / regressions |
| Recruiter | [`recruiter.md`](recruiter.md) | Hiring-signal screen |
| UX | [`ux.md`](ux.md) | Readonly UX/UI/a11y audit |

The code-review prompt lives at [`../references/code-reviewer.md`](../references/code-reviewer.md) for Antigravity `/task-loop` only. It is **not** a Cursor subagent.

## Orchestration

**`/task-loop`** (`.cursor/commands/task-loop.md`) is the only repo slash **persona** orchestrator:

```text
Manager (Assign TASK) → parent creates cursor/<slug> → Developer
```

**`/ops`** (`.cursor/commands/ops.md`) is an **operator** command: it runs existing Make targets for stacks, DB maintenance, and backups. It does not spawn personas.

- Parent Cursor chat spawns personas in order. Personas **never** spawn personas.
- Gortex is a **tool**, not a persona. On missing tools or `repo_not_tracked`, follow `.cursor/rules/gortex-workflow.mdc`.
- QA is **not** in `/task-loop`.
- There is no `/review` or `/ship` command in this repo.

## Requirement bar

When writing `requirements` / `acceptance` / `checks` (Manager Assign or human TASK):

- Each item is **one sentence** a reviewer can mark met or unmet from the diff or a named check.
- Items must be inside TASK `scope`. Do not restate `agent-workflow` or [`CODING_STANDARDS.md`](../../CODING_STANDARDS.md).
- Not a new dependency, public route, or response-contract change unless the user asked.

| Field | Means | Verdict language |
|-------|--------|------------------|
| `requirements` | Constraints on the outcome | met \| unmet |
| `acceptance` | Observable done-when behavior | met \| unmet |
| `checks` | Exact commands the developer must run (empty only for docs/prompts-only) | PASS \| FAIL \| SKIPPED |

Do not conflate them: unmet `acceptance` is not “checks failed”; empty `checks` is SKIPPED, not PASS.

## Severity schemes

**Code review** (Antigravity prompt in [`../references/code-reviewer.md`](../references/code-reviewer.md)):

| Prefix | Meaning |
|--------|---------|
| **Critical:** | Blocks merge |
| *(no prefix)* | Required — must fix before merge |
| **Nit:** | Optional |
| **Optional:** / **Consider:** | Suggestion |
| **FYI** | Informational |

**QA / Recruiter / UX findings:** Critical | High | Medium | Low (see each persona template).
