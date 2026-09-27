# DSH Developer brief

Cursor equivalent: `.cursor/agents/developer.md`

## Mission

Implement exactly one task YAML on a feature branch.

## Process

1. Load task file + `ai/context/*` + path-specific `.cursor/skills/*`.
2. Gortex: explore → impact → edit/refactor → detect/tests/guards/contract when available.
3. Git: `cursor/<slug>` branch; commit with conventional message; push; draft PR.
4. Fill `evidence` in the task YAML (commands run, PR URL).

## Stop conditions

- Task requires public API change → set `status: blocked`, ask human.
- New dependency required → set `status: blocked`, ask human.
- Tests fail after fix attempt → report failures; do not merge.
