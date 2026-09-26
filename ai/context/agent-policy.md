# Agent policy (harness)

## Git

Follow `.cursor/skills/agent-git-workflow/SKILL.md`:

- Branch: `cursor/<short-kebab-description>` (Cloud Agents may use suffix convention from run config).
- Never push to `main` unless a human explicitly requests it.

## Safety

Follow `.cursor/skills/agent-safety/SKILL.md` for commits, secrets, destructive ops, and when to run tests.

## Code intelligence

When Gortex MCP is available, follow `.cursor/rules/gortex-workflow.mdc` (explore → impact → edit → detect/tests/guards/contract).

If Gortex is unavailable, fall back to Read/Grep/Glob once; do not invent graph results.

## Roles

| Role | May change app code? | Typical output |
|------|----------------------|----------------|
| Manager | No | Task spec, acceptance criteria, specialist routing |
| Developer | Yes (on branch) | Implementation + test evidence |
| Reviewer | No | Review report (see code-reviewer framework) |
| QA | No | Repro steps, regression notes |

## Orchestration

Manager **delegates** implementation; it does not implement. Reviewer gates merge readiness; humans merge.
