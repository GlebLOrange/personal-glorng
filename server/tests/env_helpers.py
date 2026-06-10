"""Helpers for loading Settings from .env files in tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.settings import get_settings

TESTS_DIR = Path(__file__).resolve().parent
BASE_ENV_FILE = TESTS_DIR / ".env.test"
ENV_SCENARIOS_DIR = TESTS_DIR / "env"


def parse_env_lines(text: str) -> dict[str, str]:
    """Parse KEY=VALUE lines from an env file."""
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, sep, value = stripped.partition("=")
        if sep:
            values[key] = value
    return values


def write_env_file(path: Path, base: Path = BASE_ENV_FILE, **overrides: str) -> Path:
    """Write an env file from a base template with overrides."""
    values = parse_env_lines(base.read_text(encoding="utf-8"))
    values.update(overrides)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(f"{key}={value}" for key, value in values.items()) + "\n",
        encoding="utf-8",
    )
    return path


def activate_env_file(monkeypatch: pytest.MonkeyPatch, env_file: Path) -> None:
    """Point Settings at an env file (bootstrap path only) and clear cache."""
    monkeypatch.setenv("GLORNG_ENV_FILE", str(env_file.resolve()))
    get_settings.cache_clear()


def scenario_env(
    tmp_path: Path,
    *,
    base: Path = BASE_ENV_FILE,
    **overrides: str,
) -> Path:
    """Create a scenario env file under tmp_path."""
    return write_env_file(tmp_path / "scenario.env", base=base, **overrides)
