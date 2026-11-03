---
name: task-loop
description: Run the portfolio repo's bounded Manager to Developer implementation workflow when invoked as $task-loop or through the /task-loop command.
---

# Task loop

Use this project skill when invoked as `$task-loop` in Codex or when running the repo's `/task-loop` command. Treat the supplied text as the task input. This is a thin Codex entry point; read and follow `.cursor/commands/task-loop.md` as the canonical workflow for prompts, constraints, branch checks, and the final evidence format.

For prompt-caching or AI-usage tasks, also read `.cursor/skills/task-loop/references/prompt-caching.md`. Do not load that reference for unrelated tasks.

Run the Manager and Developer stages sequentially using the personas in `.cursor/agents/manager.md` and `.cursor/agents/developer.md`. Require one valid TASK YAML that meets `.cursor/agents/README.md` before starting Developer. Use the available sub-agent tool; if it is unavailable, stop and report that limitation.

The workflow requires an already active `cursor/<slug>` branch. Do not create or switch branches. Run only TASK `checks:` and stop after Developer evidence. Do not spawn QA or code review, commit, push, open a PR, or merge.
