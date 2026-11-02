#!/usr/bin/env python3
"""Rewrite dependency pins to the latest published versions.

Updates server/pyproject.toml, client/package.json, and docs/package.json,
then refreshes lockfiles. Run via `make update-deps`.

  python scripts/update_dependency_versions.py
  python scripts/update_dependency_versions.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = REPO_ROOT / "server"
CLIENT_DIR = REPO_ROOT / "client"
DOCS_DIR = REPO_ROOT / "docs"
PYPROJECT = SERVER_DIR / "pyproject.toml"

# name[extras]? followed by one or more PEP 440-ish operators
_REQ_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)"
    r"(?P<extras>\[[^\]]+\])?"
    r"(?P<spec>.+)$"
)
_SPEC_PIECE_RE = re.compile(r"(==|>=|<=|~=|!=|<|>)([^,<>=!]+)")
_NPM_RANGE_RE = re.compile(r"^(?P<op>[\^~]?)(?P<ver>.+)$")
_OTEL_PREFIX = "opentelemetry-instrumentation-"
# typescript-eslint@8 peers require typescript <6.1; do not auto-bump to TS 7+.
_NPM_SKIP_AUTO_BUMP = frozenset({"typescript"})


def version_parts(version: str) -> list[int]:
    """Return leading numeric segments of a version string."""
    parts: list[int] = []
    for segment in version.split("."):
        match = re.match(r"^(\d+)", segment)
        if match is None:
            break
        parts.append(int(match.group(1)))
        if match.end() < len(segment):
            break
    return parts


def version_lt(left: str, right: str) -> bool:
    """True when left is strictly less than right by numeric segments."""
    return version_parts(left) < version_parts(right)


def next_major(version: str) -> str:
    """Return the next major version number as a string."""
    parts = version_parts(version)
    if not parts:
        raise ValueError(f"cannot derive next major from {version!r}")
    return str(parts[0] + 1)


def rewrite_compatible_release(pinned: str, latest: str) -> str:
    """Rewrite ``X.Y.*`` / ``X.*`` to the same width from latest."""
    if not pinned.endswith(".*"):
        raise ValueError(f"not a compatible-release pin: {pinned!r}")
    width = len([p for p in pinned[:-1].split(".") if p != ""])
    latest_segments: list[str] = []
    for segment in latest.split("."):
        if len(latest_segments) >= width:
            break
        match = re.match(r"^(\d+)", segment)
        if match is None:
            break
        latest_segments.append(match.group(1))
    if len(latest_segments) < width:
        # pad with zeros if latest is shorter than the pin width
        latest_segments.extend("0" for _ in range(width - len(latest_segments)))
    return ".".join(latest_segments) + ".*"


def rewrite_python_requirement(requirement: str, latest: str) -> str:
    """Rewrite one requirement string to track ``latest``.

    Compatible-release pins keep their star width. Exact ``==`` pins become
    ``=={latest}``. Floor-only ``>=`` pins become ``>={latest}``. Bounded
    ``>=x,<y`` pins raise the floor to latest and keep the upper bound when
    latest still fits; otherwise the upper bound becomes the next major.
    """
    match = _REQ_RE.match(requirement.strip())
    if match is None:
        raise ValueError(f"unrecognized requirement: {requirement!r}")

    name = match.group("name")
    extras = match.group("extras") or ""
    spec = match.group("spec")
    pieces = list(_SPEC_PIECE_RE.finditer(spec))
    if not pieces:
        raise ValueError(f"no version specifier in {requirement!r}")

    ops = {piece.group(1): piece.group(2).strip() for piece in pieces}

    if "==" in ops and len(ops) == 1:
        pinned = ops["=="]
        if pinned.endswith(".*"):
            new_spec = f"=={rewrite_compatible_release(pinned, latest)}"
        else:
            new_spec = f"=={latest}"
        return f"{name}{extras}{new_spec}"

    if ">=" in ops and "<" in ops and set(ops) <= {">=", "<", "<="}:
        upper = ops["<"]
        if version_lt(latest, upper):
            new_upper = upper
        else:
            new_upper = next_major(latest)
        return f"{name}{extras}>={latest},<{new_upper}"

    if ">=" in ops and len(ops) == 1:
        return f"{name}{extras}>={latest}"

    raise ValueError(f"unsupported specifier shape: {requirement!r}")


def rewrite_npm_range(current: str, latest: str) -> str:
    """Keep ``^`` / ``~`` (or none) and point the version at ``latest``."""
    match = _NPM_RANGE_RE.match(current.strip())
    if match is None:
        raise ValueError(f"unrecognized npm range: {current!r}")
    return f"{match.group('op')}{latest}"


def distribution_name(requirement: str) -> str:
    """Return the distribution name from a requirement string."""
    match = _REQ_RE.match(requirement.strip())
    if match is None:
        raise ValueError(f"unrecognized requirement: {requirement!r}")
    return match.group("name")


def fetch_pypi_latest(name: str) -> str:
    """Return the latest version published on PyPI for ``name``."""
    url = f"https://pypi.org/pypi/{name}/json"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"PyPI lookup failed for {name}: HTTP {exc.code}") from exc
    version = payload.get("info", {}).get("version")
    if not isinstance(version, str) or not version:
        raise RuntimeError(f"PyPI returned no version for {name}")
    return version


def fetch_npm_latest(name: str) -> str:
    """Return the latest version published on npm for ``name``."""
    result = subprocess.run(
        ["npm", "view", name, "version"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"npm view failed for {name}: {detail}")
    version = result.stdout.strip()
    if not version:
        raise RuntimeError(f"npm view returned empty version for {name}")
    return version


def collect_python_requirements(text: str) -> list[str]:
    """Collect pinned requirements via tomllib (handles extras brackets)."""
    data = tomllib.loads(text)
    reqs: list[str] = list(data.get("project", {}).get("dependencies", []))
    reqs.extend(data.get("dependency-groups", {}).get("dev", []))
    reqs.extend(
        data.get("tool", {}).get("uv", {}).get("override-dependencies", [])
    )
    return reqs


def apply_python_updates(text: str, updates: dict[str, str]) -> str:
    """Replace quoted requirement strings; longest keys first to avoid clashes."""
    updated = text
    for old, new in sorted(updates.items(), key=lambda item: -len(item[0])):
        if old == new:
            continue
        needle = f'"{old}"'
        if needle not in updated:
            raise RuntimeError(f"could not find requirement {old!r} in pyproject.toml")
        updated = updated.replace(needle, f'"{new}"', 1)
    return updated


def update_package_json(path: Path, dry_run: bool) -> list[tuple[str, str, str]]:
    """Rewrite dependency ranges in a package.json; return change triples."""
    data = json.loads(path.read_text(encoding="utf-8"))
    changes: list[tuple[str, str, str]] = []
    for field in ("dependencies", "devDependencies"):
        block = data.get(field)
        if not isinstance(block, dict):
            continue
        for name, current in list(block.items()):
            if not isinstance(current, str):
                continue
            if name in _NPM_SKIP_AUTO_BUMP:
                continue
            latest = fetch_npm_latest(name)
            rewritten = rewrite_npm_range(current, latest)
            if rewritten == current:
                continue
            changes.append((name, current, rewritten))
            block[name] = rewritten
    if changes and not dry_run:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return changes


def refresh_uv_lock() -> None:
    """Upgrade the uv lockfile after pin rewrites."""
    subprocess.run(["uv", "lock", "--upgrade"], cwd=SERVER_DIR, check=True)


def refresh_npm_lock(directory: Path) -> None:
    """Refresh package-lock.json for ``directory``.

    Client TypeScript stays on ~5.9.x for typescript-eslint peer compatibility.
    """
    subprocess.run(
        ["npm", "install"],
        cwd=directory,
        check=True,
    )


def resolve_otel_version(latest_by_name: dict[str, str]) -> str | None:
    """Return one shared version for all opentelemetry-instrumentation-* pins.

    Uses the minimum of each package's PyPI latest so every distribution can
    share the same pin. Returns None when no OTEL instrumentation deps exist.
    """
    otel = {
        name: version
        for name, version in latest_by_name.items()
        if name.lower().startswith(_OTEL_PREFIX)
    }
    if not otel:
        return None
    return min(otel.values(), key=version_parts)


def update_python(dry_run: bool) -> list[tuple[str, str, str]]:
    """Rewrite pyproject pins; return (name, old, new) change triples."""
    text = PYPROJECT.read_text(encoding="utf-8")
    requirements = collect_python_requirements(text)
    latest_by_name: dict[str, str] = {}
    updates: dict[str, str] = {}
    changes: list[tuple[str, str, str]] = []

    for requirement in requirements:
        name = distribution_name(requirement)
        if name not in latest_by_name:
            latest_by_name[name] = fetch_pypi_latest(name)

    otel_version = resolve_otel_version(latest_by_name)
    otel_forced = False
    if otel_version is not None:
        otel_latests = {
            version
            for name, version in latest_by_name.items()
            if name.lower().startswith(_OTEL_PREFIX)
        }
        otel_forced = len(otel_latests) > 1
        if otel_forced:
            lagging = sorted(
                name
                for name, version in latest_by_name.items()
                if name.lower().startswith(_OTEL_PREFIX)
                and version == otel_version
            )
            ahead = sorted(
                f"{name}={version}"
                for name, version in latest_by_name.items()
                if name.lower().startswith(_OTEL_PREFIX)
                and version != otel_version
            )
            print(
                "  note: aligning opentelemetry-instrumentation-* to "
                f"{otel_version} (limited by {', '.join(lagging)}; "
                f"newer on PyPI: {', '.join(ahead)})"
            )
            print(
                "  note: leaving fastapi and elastic-opentelemetry unchanged "
                "while instrumentation cannot move in lockstep"
            )

    for requirement in requirements:
        name = distribution_name(requirement)
        if (
            otel_version is not None
            and name.lower().startswith(_OTEL_PREFIX)
        ):
            latest = otel_version
        elif otel_forced and name.lower() in {
            "elastic-opentelemetry",
            "fastapi",
        }:
            # These track OTEL API/convention pins; leave them alone when
            # instrumentation cannot move in lockstep (e.g. elasticsearch).
            updates[requirement] = requirement
            continue
        else:
            latest = latest_by_name[name]
        rewritten = rewrite_python_requirement(requirement, latest)
        updates[requirement] = rewritten
        if rewritten != requirement:
            changes.append((name, requirement, rewritten))

    if changes and not dry_run:
        PYPROJECT.write_text(apply_python_updates(text, updates), encoding="utf-8")
    return changes


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned pin changes without writing or refreshing locks",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Update Python and npm pins, then refresh lockfiles."""
    args = parse_args(argv)

    print("Python (server/pyproject.toml)")
    py_changes = update_python(dry_run=args.dry_run)
    if not py_changes:
        print("  (no pin changes)")
    for name, old, new in py_changes:
        print(f"  {name}: {old} -> {new}")

    print("npm (client/package.json)")
    client_changes = update_package_json(CLIENT_DIR / "package.json", dry_run=args.dry_run)
    if not client_changes:
        print("  (no pin changes)")
    for name, old, new in client_changes:
        print(f"  {name}: {old} -> {new}")

    print("npm (docs/package.json)")
    docs_changes = update_package_json(DOCS_DIR / "package.json", dry_run=args.dry_run)
    if not docs_changes:
        print("  (no pin changes)")
    for name, old, new in docs_changes:
        print(f"  {name}: {old} -> {new}")

    if args.dry_run:
        print("dry-run: skipped lockfile refresh")
        return 0

    print("Refreshing server/uv.lock")
    refresh_uv_lock()
    print("Refreshing client/package-lock.json")
    refresh_npm_lock(CLIENT_DIR)
    print("Refreshing docs/package-lock.json")
    refresh_npm_lock(DOCS_DIR)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        raise SystemExit(1) from exc
