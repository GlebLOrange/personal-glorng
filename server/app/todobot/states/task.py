from aiogram.fsm.state import State, StatesGroup


class TaskCreation(StatesGroup):
    """FSM states for AI intake and guided task creation."""

    waiting_for_input = State()
    clarifying = State()
    waiting_for_title = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_location = State()
    waiting_for_notes = State()
    waiting_for_reminder = State()
    confirming = State()


class TaskPostpone(StatesGroup):
    """FSM state for rescheduling a task from a reminder action."""

    waiting_for_datetime = State()
