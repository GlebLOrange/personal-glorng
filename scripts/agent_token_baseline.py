#!/usr/bin/env python3
"""Estimate always-on Cursor agent context size (chars ÷ 4 ≈ tokens).

Not provider billing — a comparable pre/post metric for repo-controlled static context.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN_DIVISOR = 4
COMMUNITIES_RE = re.compile(
    r"<!-- gortex:communities:start -->.*?<!-- gortex:communities:end -->",
    re.DOTALL,
)


@dataclass(frozen=True)
class Row:
    """One sized context source."""

    label: str
    path: str
    chars: int
    note: str = ""

    @property
    def tokens(self) -> int:
        """Rounded token estimate."""
        return (self.chars + TOKEN_DIVISOR - 1) // TOKEN_DIVISOR


def _read(path: Path) -> str:
    """Read UTF-8 text; missing file → empty."""
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _skill_catalog_chars(skills_dir: Path) -> tuple[int, int, int]:
    """Return (all, gortex-*, product) catalog description chars from SKILL.md fronts."""
    all_c = gortex_c = product_c = 0
    if not skills_dir.is_dir():
        return 0, 0, 0
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        text = _read(skill_md)
        # Catalog usually exposes name + description from frontmatter.
        name_m = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
        desc_m = re.search(
            r"^description:\s*(?:>-\s*)?(?:\"([^\"]*)\"|'([^']*)'|(.*))$",
            text,
            re.MULTILINE,
        )
        name = (name_m.group(1).strip() if name_m else skill_md.parent.name)
        if desc_m:
            desc = (desc_m.group(1) or desc_m.group(2) or desc_m.group(3) or "").strip()
        else:
            desc = ""
        # Folded YAML descriptions may span lines; take first ~400 chars of body after ---
        if not desc or desc.endswith("|"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                fm = parts[1]
                dm = re.search(r"description:\s*>-?\s*\n((?:  .+\n)+)", fm)
                if dm:
                    desc = " ".join(line.strip() for line in dm.group(1).splitlines())
        entry = f"{name}: {desc}"
        n = len(entry)
        all_c += n
        if skill_md.parent.name.startswith("gortex-"):
            gortex_c += n
        else:
            product_c += n
    return all_c, gortex_c, product_c


def _session_start_inject_chars() -> int:
    """Chars of the injected context template (branch placeholder counted)."""
    script = _read(ROOT / ".cursor" / "hooks" / "session-start.sh")
    m = re.search(r'context = f?"""(.*?)"""', script, re.DOTALL)
    if m:
        return len(m.group(1).replace("{branch}", "cursor/example-branch"))
    # context = ( f"..." "..." ) form
    m = re.search(
        r"context\s*=\s*\(\s*(.*?)\s*\)\s*\n\s*env\s*=",
        script,
        re.DOTALL,
    )
    if not m:
        return 0
    parts = re.findall(r'f?"((?:\\.|[^"\\])*)"', m.group(1))
    joined = "".join(parts).replace("{branch}", "cursor/example-branch")
    return len(joined)


def collect() -> list[Row]:
    """Collect sized rows for always-on / catalog sources."""
    rows: list[Row] = []
    rules = ROOT / ".cursor" / "rules"
    for name in (
        "gortex-workflow.mdc",
        "gortex-communities.mdc",
        "project-context.mdc",
        "agent-workflow.mdc",
    ):
        path = rules / name
        text = _read(path)
        rows.append(Row(name, str(path.relative_to(ROOT)), len(text)))

    agents = _read(ROOT / "AGENTS.md")
    rows.append(Row("AGENTS.md (full)", "AGENTS.md", len(agents)))
    communities = COMMUNITIES_RE.findall(agents)
    c_chars = sum(len(b) for b in communities)
    rows.append(
        Row(
            "AGENTS.md communities block",
            "AGENTS.md",
            c_chars,
            "dedupe candidate",
        ),
    )

    for extra in ("GEMINI.md", ".github/copilot-instructions.md"):
        text = _read(ROOT / extra)
        blocks = COMMUNITIES_RE.findall(text)
        rows.append(
            Row(
                f"{extra} communities",
                extra,
                sum(len(b) for b in blocks),
                "mirror",
            ),
        )

    all_c, gortex_c, product_c = _skill_catalog_chars(ROOT / ".cursor" / "skills")
    rows.append(Row("skill catalog (all)", ".cursor/skills/*/SKILL.md", all_c))
    rows.append(Row("skill catalog (gortex-*)", ".cursor/skills/gortex-*", gortex_c))
    rows.append(Row("skill catalog (product)", ".cursor/skills (non-gortex)", product_c))

    inject = _session_start_inject_chars()
    rows.append(
        Row(
            "sessionStart inject",
            ".cursor/hooks/session-start.sh",
            inject,
            "volatile",
        ),
    )

    refs = ROOT / ".cursor" / "references" / "gortex-skills"
    if refs.is_dir():
        n = len(list(refs.glob("*/SKILL.md")))
        rows.append(
            Row(
                "offloaded gortex skills (count)",
                str(refs.relative_to(ROOT)),
                n,
                "dirs counted as chars=count for visibility",
            ),
        )

    return rows


def main() -> int:
    """Print a markdown table of estimates."""
    rows = collect()
    static = sum(
        r.tokens
        for r in rows
        if r.label
        in {
            "gortex-workflow.mdc",
            "gortex-communities.mdc",
            "project-context.mdc",
            "agent-workflow.mdc",
            "AGENTS.md (full)",
            "skill catalog (all)",
            "sessionStart inject",
        }
    )
    print(f"# Agent token baseline (chars÷{TOKEN_DIVISOR})")
    print()
    print("| Source | Path | Chars | ~Tokens | Note |")
    print("|--------|------|------:|--------:|------|")
    for r in rows:
        note = r.note or ""
        print(f"| {r.label} | `{r.path}` | {r.chars} | {r.tokens} | {note} |")
    print()
    print(f"**Sum of primary always-on rows:** ~{static} tokens")
    print()
    print(
        "Primary always-on = alwaysApply rules + full AGENTS.md + skill catalog + sessionStart.",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
