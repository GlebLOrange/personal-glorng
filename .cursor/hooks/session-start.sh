#!/usr/bin/env bash
set -euo pipefail

branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"

python3 - <<'PY' "$branch"
import json
import sys

branch = sys.argv[1]
context = f"""Git workflow for this repository:
- Base branch: main
- Create a feature branch before making code changes unless already on cursor/* or an explicit feature branch
- Branch naming: cursor/<short-kebab-description> (example: cursor/groq-only-ai-chat)
- If the user starts a task on main, ask once: create branch cursor/<name> now? Then run git checkout -b before editing
- Prefer isolated work via Worktree (/worktree) or Agents window Worktree location when starting a new chat
- Do not commit or push to main unless the user explicitly asks
- Current branch: {branch}"""

print(json.dumps({"additional_context": context}))
PY
