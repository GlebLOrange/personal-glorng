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
