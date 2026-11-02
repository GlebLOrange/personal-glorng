#!/usr/bin/env bash
set -euo pipefail

# afterFileEdit: mark this composer session as having agent edits (for gated micro-save).
# Stdin payload is unused beyond consuming it; session id comes from sessionStart env.
cat >/dev/null || true

python3 - <<'PY'
import json
import os
import re
from pathlib import Path

session = os.environ.get("PORTFOLIO_CTX_SESSION") or "unknown"
safe = re.sub(r"[^A-Za-z0-9._-]+", "_", session)[:120] or "unknown"
path = Path(os.environ.get("TMPDIR") or "/tmp") / "portfolio-glorng-ctx" / f"{safe}.state"
path.parent.mkdir(parents=True, exist_ok=True)

state = {"edited": True, "prompted": False}
if path.is_file():
    try:
        prev = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(prev, dict) and prev.get("prompted"):
            state["prompted"] = True
    except (OSError, json.JSONDecodeError):
        pass

path.write_text(json.dumps(state) + "\n", encoding="utf-8")
print("{}")
PY
