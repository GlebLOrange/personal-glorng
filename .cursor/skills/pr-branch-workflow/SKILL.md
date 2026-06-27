---
name: pr-branch-workflow
description: Guides agents through creating a branch from main, committing changes, pushing, opening a PR, resolving conflicts, and preparing a squash merge. Use when the user asks to create a branch, commit and push changes, create a pull request, fix PR conflicts, or merge/squash a PR.
---

# PR Branch Workflow

## Instructions

Use this workflow when the user asks to take local work from branch creation through PR preparation.

1. Start from `main` unless the user names another base branch.
2. Check `git status --short` and identify unrelated or user-owned changes before switching branches.
3. Create a feature branch named `cursor/<short-kebab-description>`.
4. Make or verify the requested changes only. Do not include unrelated files.
5. Before committing, run in parallel:
   - `git status`
   - `git diff`
   - `git log --oneline -5`
6. Stage only the files needed for the request.
7. Commit with a concise message via HEREDOC.
8. Push with `git push -u origin HEAD` only when the user asked to push or open a PR.
9. Create the PR with `gh pr create`, using a short title and a body with `Summary` and `Test plan`.
10. If GitHub reports conflicts, resolve them by preserving the requested change and the latest base branch behavior. Ask before discarding any user-owned change.
11. After conflict resolution, rerun targeted verification and push the conflict fix.
12. Do not merge, squash, or enable auto-merge unless the user explicitly approves that final action in the current conversation.

## Merge Rule

When squash merge is available, tell the user it is ready and ask for approval before running `gh pr merge --squash` or equivalent.

## Safety

- Never force push unless the user explicitly requests it.
- Never push to `main`.
- Never commit `.env`, credentials, tokens, or secret-bearing files.
- Never use `--no-verify` unless the user explicitly requests it.
- Keep unrelated untracked files out of the commit and PR.
