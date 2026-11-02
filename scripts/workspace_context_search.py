#!/usr/bin/env python3
"""Keyword search over .cursor/workspace-context/index.yaml (+ sessions/*.md).

Usage: python3 scripts/workspace_context_search.py <keyword> [keyword ...]
Prints at most 3 matching entries (~5-20 lines). No PyYAML dependency.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / ".cursor" / "workspace-context"
MAX_HITS = 3


def index_entries() -> list[str]:
    path = ROOT / "index.yaml"
    if not path.exists():
        return []
    text = "\n".join(line for line in path.read_text().splitlines() if not line.lstrip().startswith("#"))
    return [b.strip() for b in re.split(r"\n(?=\s*- date:)", text) if "date:" in b]


def session_entries() -> list[str]:
    d = ROOT / "sessions"
    if not d.is_dir():
        return []
    out = []
    for f in sorted(d.glob("*.md"), reverse=True):
        lines = f.read_text().splitlines()[:8]
        out.append(f"# {f.name}\n" + "\n".join(lines))
    return out


def main(argv: list[str]) -> int:
    words = [w.lower() for w in argv if w.strip()]
    if not words:
        print(__doc__.strip())
        return 2
    scored = []
    for e in index_entries() + session_entries():
        low = e.lower()
        score = sum(low.count(w) for w in words)
        if score:
            scored.append((score, e))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print("No matching workspace-context entries.")
        return 0
    for _, e in scored[:MAX_HITS]:
        print("\n".join(e.splitlines()[:7]))
        print("---")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
