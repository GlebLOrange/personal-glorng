from aiogram.fsm.state import State, StatesGroup


class ExpenseCreation(StatesGroup):
    """FSM states for guided expense logging."""

    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_place = State()
    confirming = State()
