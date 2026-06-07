"""Smoke tests for seed module imports (no DB side effects)."""


def test_seed_builders_imports() -> None:
    from app.db.seed import builders

    assert builders.EXPENSE_CATEGORIES
    assert builders.EXPENSE_CURRENCIES


def test_seed_run_imports() -> None:
    from app.db.seed.run import seed

    assert callable(seed)
