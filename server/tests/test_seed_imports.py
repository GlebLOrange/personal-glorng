"""Smoke tests for seed module imports (no DB side effects)."""


def test_seed_builders_imports() -> None:
    from app.db.seed import builders

    assert builders.EXPENSE_CATEGORIES
    assert builders.EXPENSE_CURRENCIES


def test_seed_run_imports() -> None:
    from app.db.seed.run import seed

    assert callable(seed)


def test_demo_builders_imports() -> None:
    from app.db.seed import demo_builders

    assert demo_builders.DEMO_READER_EMAIL
    assert demo_builders.demo_reader_permissions()
    assert demo_builders.demo_writer_permissions()


def test_seed_demo_imports() -> None:
    from app.db.seed.demo import seed_demo
    from app.db.seed_demo import main, parse_args

    assert callable(seed_demo)
    assert callable(main)
    assert callable(parse_args)
