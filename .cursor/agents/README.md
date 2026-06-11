# Agent Personas

Custom agent definitions for this repository live in `.cursor/agents/`.

## Available personas

| Persona | File | Use when |
|---------|------|----------|
| Code reviewer | [`code-reviewer.mdc`](code-reviewer.mdc) | Thorough five-axis review before merge |

## Composition

- **Invoke directly** when the user asks for a review of a specific change, file, or PR.
- **Do not invoke from another persona.** If a persona wants specialized security or test coverage, surface that as a recommendation in the report — orchestration belongs to slash commands, not nested persona calls.

## Severity labels

Findings use the same scheme as [`code-review-and-quality.mdc`](../rules/code-review-and-quality.mdc):

| Prefix | Meaning |
|--------|---------|
| **Critical:** | Blocks merge |
| *(no prefix)* | Required — must fix before merge |
| **Nit:** | Minor, optional |
| **Optional:** / **Consider:** | Suggestion |
| **FYI** | Informational only |
