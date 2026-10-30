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
context = (
    f"Current branch: {branch}. "
    "Git branch workflow: .cursor/skills/agent-workflow/SKILL.md"
)

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
