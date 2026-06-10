"""Smoke tests for seed module imports (no DB side effects)."""


def test_seed_builders_imports() -> None:
    from app.db.seed.builders import EXPENSE_CATEGORIES, EXPENSE_CURRENCIES

    assert EXPENSE_CATEGORIES
    assert EXPENSE_CURRENCIES


def test_seed_run_imports() -> None:
    from app.db.seed import seed

    assert callable(seed)


def test_demo_builders_imports() -> None:
    from app.db.seed.builders.demo import (
        DEMO_READER_EMAIL,
        demo_reader_permissions,
        demo_writer_permissions,
    )

    assert DEMO_READER_EMAIL
    assert demo_reader_permissions()
    assert demo_writer_permissions()


def test_seed_demo_imports() -> None:
    from app.db.seed.demo import seed_demo
    from app.db.seed_demo import main, parse_args

    assert callable(seed_demo)
    assert callable(main)
    assert callable(parse_args)


def test_seed_demo_module_invokes_main() -> None:
    """`python -m app.db.seed_demo` must expose the CLI (db_init RUN_SEED depends on this)."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "app.db.seed_demo", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--skip-if-populated" in result.stdout
