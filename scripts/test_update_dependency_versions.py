#!/usr/bin/env python3
"""Assert-only checks for dependency pin rewrite rules. No network."""

from __future__ import annotations

from update_dependency_versions import (
    resolve_otel_version,
    rewrite_compatible_release,
    rewrite_npm_range,
    rewrite_python_requirement,
)


def test_compatible_release_width() -> None:
    """Star width is preserved from the existing pin."""
    assert rewrite_compatible_release("0.52.*", "0.55.1") == "0.55.*"
    assert rewrite_compatible_release("2.*", "2.15.0") == "2.*"
    assert rewrite_compatible_release("0.0.*", "0.0.35") == "0.0.*"
    assert rewrite_compatible_release("69.*", "69.0") == "69.*"
    assert (
        rewrite_python_requirement("uvicorn[standard]==0.52.*", "0.55.1")
        == "uvicorn[standard]==0.55.*"
    )
    assert rewrite_python_requirement("pydantic[email]==2.*", "2.12.0") == (
        "pydantic[email]==2.*"
    )


def test_exact_pin() -> None:
    """Exact equality pins become =={latest}."""
    assert (
        rewrite_python_requirement(
            "opentelemetry-instrumentation-fastapi==0.64b0",
            "0.65b0",
        )
        == "opentelemetry-instrumentation-fastapi==0.65b0"
    )


def test_floor_only() -> None:
    """Floor-only >= pins raise the floor to latest."""
    assert rewrite_python_requirement("yt-dlp>=2026.8.19", "2026.9.1") == (
        "yt-dlp>=2026.9.1"
    )
    assert rewrite_python_requirement("mypy>=2.3.1", "2.4.0") == "mypy>=2.4.0"
    assert rewrite_python_requirement("firebase-admin>=7.5.0", "7.6.0") == (
        "firebase-admin>=7.6.0"
    )


def test_bounded_range() -> None:
    """Bounded ranges keep upper when latest fits; otherwise bump next major."""
    assert rewrite_python_requirement("segno>=1.6,<2", "1.6.6") == "segno>=1.6.6,<2"
    assert rewrite_python_requirement("segno>=1.6,<2", "2.0.0") == "segno>=2.0.0,<3"
    assert rewrite_python_requirement("aiohttp>=3.14.0", "3.15.1") == (
        "aiohttp>=3.15.1"
    )


def test_npm_operators() -> None:
    """npm rewrite keeps ^ / ~ and points at latest."""
    assert rewrite_npm_range("^3.5.43", "3.5.50") == "^3.5.50"
    assert rewrite_npm_range("~7.0.2", "7.0.5") == "~7.0.5"
    assert rewrite_npm_range("1.2.3", "1.2.4") == "1.2.4"


def test_otel_alignment() -> None:
    """OTEL instrumentation pins share the minimum latest."""
    shared = resolve_otel_version(
        {
            "opentelemetry-instrumentation-fastapi": "0.66b0",
            "opentelemetry-instrumentation-elasticsearch": "0.64b0",
            "fastapi": "0.141.0",
        }
    )
    assert shared == "0.64b0"
    assert resolve_otel_version({"fastapi": "0.141.0"}) is None


def main() -> None:
    """Run all assert checks."""
    test_compatible_release_width()
    test_exact_pin()
    test_floor_only()
    test_bounded_range()
    test_npm_operators()
    test_otel_alignment()
    print("ok")


if __name__ == "__main__":
    main()
