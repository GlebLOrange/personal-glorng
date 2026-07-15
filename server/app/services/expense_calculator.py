"""Persist expense calculator snapshots for superusers."""

from datetime import UTC, datetime

from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.schemas.expense_calculator import ExpenseCalculatorState

EXPENSE_CALCULATOR_PREF_KEY = "expense_calculator"


def get_calculator_state(user: User) -> ExpenseCalculatorState | None:
    """Return saved calculator state or None when unset."""
    raw = (user.preferences or {}).get(EXPENSE_CALCULATOR_PREF_KEY)
    if not isinstance(raw, dict):
        return None
    try:
        return ExpenseCalculatorState.model_validate(raw)
    except Exception:
        return None


async def save_calculator_state(
    registry: DatabaseRegistry,
    user: User,
    state: ExpenseCalculatorState,
) -> ExpenseCalculatorState:
    """Upsert calculator snapshot on the user document."""
    current = dict(user.preferences or {})
    payload = state.model_copy(
        update={"saved_at": datetime.now(tz=UTC)},
    ).model_dump(mode="json")
    current[EXPENSE_CALCULATOR_PREF_KEY] = payload
    await registry.users.update_fields(user.id, preferences=current)  # type: ignore[union-attr]
    return ExpenseCalculatorState.model_validate(payload)
