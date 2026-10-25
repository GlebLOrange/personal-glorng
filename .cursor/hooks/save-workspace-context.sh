#!/usr/bin/env bash
set -euo pipefail

# Stop hook: after a completed agent turn, request one micro-save.
# Stdin is the stop payload; pass it as an argv because the heredoc replaces stdin.
input="$(cat)"

python3 - <<'PY' "$input"
import json
import sys

raw = sys.argv[1] if len(sys.argv) > 1 else ""
try:
    payload = json.loads(raw) if raw.strip() else {}
except json.JSONDecodeError:
    print("{}")
    raise SystemExit(0)

status = payload.get("status")
try:
    loop_count = int(payload.get("loop_count", 0))
except (TypeError, ValueError):
    loop_count = 0

if status != "completed" or loop_count > 0:
    print("{}")
    raise SystemExit(0)

followup = (
    "Micro-save only (saving-workspace-context). "
    "If this turn produced a durable decision or non-obvious constraint, "
    "append one short dated line to the first matching home from that skill "
    "and mention the path. "
    "Do not create skills, rules, or new files; do not commit or push; "
    "do not save secrets, logs, or anything obvious from the code. "
    "If nothing durable, edit nothing and reply exactly: "
    "No workspace context to save."
)
print(json.dumps({"followup_message": followup}))
PY
