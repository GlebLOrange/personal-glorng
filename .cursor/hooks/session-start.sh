#!/usr/bin/env bash
set -euo pipefail

# Session start: inject git branch context + export session id for later hooks.
# Stdin is the sessionStart payload; pass it as argv because the heredoc replaces stdin.
host="${1:-cursor}"
branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
input="$(cat)"

python3 - <<'PY' "$branch" "$host" "$input"
import json
import sys

branch = sys.argv[1]
host = sys.argv[2]
raw = sys.argv[3] if len(sys.argv) > 3 else ""
try:
    payload = json.loads(raw) if raw.strip() else {}
except json.JSONDecodeError:
    payload = {}

session_id = str(payload.get("session_id") or "unknown")
context = f"""Git workflow for this repository:
- Base branch: main
- Create a feature branch before making code changes unless already on cursor/* or an explicit feature branch
- Branch naming: cursor/<short-kebab-description> (example: cursor/groq-only-ai-chat)
- If the user starts a task on main, ask once: create branch cursor/<name> now? Then run git checkout -b before editing
- Prefer isolated work via Worktree (/worktree) or Agents window Worktree location when starting a new chat
- Do not commit or push to main unless the user explicitly asks
- Current branch: {branch}"""

env = {"PORTFOLIO_CTX_SESSION": session_id}

if host == "antigravity":
    print(
        json.dumps(
            {
                "injectSteps": [
                    {"systemMessage": {"systemMessage": context}},
                ],
                "env": env,
            }
        )
    )
elif host == "claude":
    print(json.dumps({"additionalContext": context, "env": env}))
else:
    print(json.dumps({"additional_context": context, "env": env}))
PY
