# Agent Personas

Custom agent definitions for this repository live in `.cursor/agents/`.

## Available personas

| Persona | File | Use when |
|---------|------|----------|
| Code reviewer | [`code-reviewer.mdc`](code-reviewer.mdc) | Thorough five-axis review before merge |
| Manager | [`manager.md`](manager.md) | Prioritize next portfolio work and coordinate specialists |
| QA | [`qa.md`](qa.md) | Find reproducible bugs (do not change app code) |
| Recruiter | [`recruiter.md`](recruiter.md) | Screen the site for Python/backend hiring signal |
| UX | [`ux.md`](ux.md) | Audit UI, usability, and accessibility (do not change app code) |

## Composition

- **Invoke directly** when the user asks for a review of a specific change, file, or PR.
- **Do not invoke from another persona.** If a persona wants specialized security or test coverage, surface that as a recommendation in the report — orchestration belongs to slash commands, not nested persona calls.

## Severity labels

Findings use the same scheme as [`code-review-and-quality`](../skills/code-review-and-quality/SKILL.md):

| Prefix | Meaning |
|--------|---------|
| **Critical:** | Blocks merge |
| *(no prefix)* | Required — must fix before merge |
| **Nit:** | Minor, optional |
| **Optional:** / **Consider:** | Suggestion |
| **FYI** | Informational only |
