#!/usr/bin/env bash
set -euo pipefail

# Stop hook: at most one micro-save per session, and only after agent file edits.
# Stdin is the stop payload; pass it as an argv because the heredoc replaces stdin.
input="$(cat)"

python3 - <<'PY' "$input"
import json
import os
import re
import sys
from pathlib import Path

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

session = os.environ.get("PORTFOLIO_CTX_SESSION") or "unknown"
safe = re.sub(r"[^A-Za-z0-9._-]+", "_", session)[:120] or "unknown"
path = Path(os.environ.get("TMPDIR") or "/tmp") / "portfolio-glorng-ctx" / f"{safe}.state"

state = {"edited": False, "prompted": False}
if path.is_file():
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            state["edited"] = bool(loaded.get("edited"))
            state["prompted"] = bool(loaded.get("prompted"))
    except (OSError, json.JSONDecodeError):
        pass

if not state["edited"] or state["prompted"]:
    print("{}")
    raise SystemExit(0)

path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps({"edited": True, "prompted": True}) + "\n", encoding="utf-8")

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
