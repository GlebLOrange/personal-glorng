"""My tasks two-level menu: list → detail → remove / edit date-time."""

from contextlib import suppress
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.core.exceptions import ConflictError
from app.core.utils import as_utc, format_scheduled_at, local_naive_to_utc, local_now
from app.db.documents.audit import AuditActorType, AuditSource
from app.db.documents.task import Task, TaskStatus
from app.db.registry import DatabaseRegistry
from app.services.task import (
    change_status,
    get_closest_pending_tasks,
    get_task,
    reschedule_task,
    sync_calendar_for_telegram_user,
    update_task_details,
)
from app.settings import get_settings
from app.todobot.keyboards.task import (
    my_task_date_picker,
    my_task_detail,
    my_task_edit_fields,
    my_task_remove_choices,
    my_task_time_picker,
    my_tasks_list,
)
from app.todobot.states.task import TaskBrowse
from app.todobot.utils.markdown import escape_md
from app.todobot.utils.nlp import parse_task_input

router = Router()

_CLOSEST_LIMIT = 7
_SCREEN_MSG_KEY = "mtask_screen_msg_id"
_EDIT_TASK_KEY = "mtask_edit_task_id"
_EDIT_DATE_KEY = "mtask_edit_date"

_REMOVE_STATUS = {
    "cancelled": TaskStatus.CANCELLED,
    "not_completed": TaskStatus.NOT_COMPLETED,
}


def _task_button_label(task: Task) -> str:
    scheduled = format_scheduled_at(task.scheduled_at) if task.scheduled_at else "—"
    return f"{task.title} — {scheduled}"


def _detail_text(task: Task) -> str:
    scheduled = format_scheduled_at(task.scheduled_at) if task.scheduled_at else "—"
    lines = [
        f"*{escape_md(task.title)}*",
        f"When: {scheduled}",
    ]
    if task.location:
        lines.append(f"Where: {escape_md(task.location)}")
    if task.description:
        lines.append(f"Notes: {escape_md(task.description)}")
    return "\n".join(lines)


def _split_overdue_upcoming(tasks: list[Task]) -> tuple[list[Task], list[Task]]:
    now = local_now()
    tz = ZoneInfo(get_settings().TIMEZONE)
    overdue: list[Task] = []
    upcoming: list[Task] = []
    for task in tasks:
        if task.scheduled_at and as_utc(task.scheduled_at).astimezone(tz) < now:
            overdue.append(task)
        else:
            upcoming.append(task)
    return overdue, upcoming


async def _calendar_connected(
    registry: DatabaseRegistry,
    telegram_user_id: int,
) -> bool:
    if registry.credentials is None:
        return False
    cred = await registry.credentials.get_google_for_telegram_user(telegram_user_id)
    return cred is not None


async def _delete_screen(
    *,
    bot: object | None,
    chat_id: int,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    msg_id = data.get(_SCREEN_MSG_KEY)
    if msg_id and bot is not None:
        with suppress(Exception):
            await bot.delete_message(chat_id, msg_id)  # type: ignore[union-attr]
    await state.update_data(**{_SCREEN_MSG_KEY: None})


async def _show_list(
    *,
    message: Message,
    registry: DatabaseRegistry,
    state: FSMContext,
    edit: bool = False,
) -> None:
    if not message.from_user:
        return

    telegram_user_id = message.from_user.id
    connected = await _calendar_connected(registry, telegram_user_id)
    if connected:
        await sync_calendar_for_telegram_user(
            registry,
            telegram_user_id=telegram_user_id,
        )

    tasks = await get_closest_pending_tasks(
        registry,
        telegram_user_id=telegram_user_id,
        limit=_CLOSEST_LIMIT,
    )

    header = "*Your closest tasks:*"
    if not connected:
        header = (
            "*Your closest tasks:*\n_Calendar not connected — tap Calendar to link._"
        )

    if not tasks:
        text = f"{header}\n\nNo pending tasks. Use Quick or Guided to add one."
        markup = None
    else:
        overdue, upcoming = _split_overdue_upcoming(tasks)
        lines = [header, ""]
        buttons: list[tuple[int, str]] = []
        if overdue:
            lines.append("*Overdue:*")
            for task in overdue:
                lines.append(f"• {_task_button_label(task)}")
                buttons.append((task.id, f"⚠ {_task_button_label(task)}"))
            lines.append("")
        if upcoming:
            lines.append("*Upcoming:*")
            for task in upcoming:
                lines.append(f"• {_task_button_label(task)}")
                buttons.append((task.id, _task_button_label(task)))
        text = "\n".join(lines)
        markup = my_tasks_list(buttons)

    await state.set_state(TaskBrowse.browsing)

    if edit and message.bot:
        with suppress(Exception):
            await message.edit_text(text, parse_mode="Markdown", reply_markup=markup)
            await state.update_data(**{_SCREEN_MSG_KEY: message.message_id})
            return

    await _delete_screen(bot=message.bot, chat_id=message.chat.id, state=state)
    sent = await message.answer(text, parse_mode="Markdown", reply_markup=markup)
    await state.update_data(**{_SCREEN_MSG_KEY: sent.message_id})


async def _show_detail(
    *,
    callback: CallbackQuery,
    task: Task,
    state: FSMContext,
) -> None:
    if not callback.message:
        return
    text = _detail_text(task)
    markup = my_task_detail(task.id)
    await state.set_state(TaskBrowse.browsing)
    with suppress(Exception):
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=markup,
        )
        await state.update_data(**{_SCREEN_MSG_KEY: callback.message.message_id})
        return
    await _delete_screen(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        state=state,
    )
    sent = await callback.message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=markup,
    )
    await state.update_data(**{_SCREEN_MSG_KEY: sent.message_id})


async def _owned_task(
    registry: DatabaseRegistry,
    *,
    task_id: int,
    telegram_user_id: int,
) -> Task | None:
    task = await get_task(registry, task_id=task_id)
    if not task or task.telegram_user_id != telegram_user_id:
        return None
    return task


async def open_task_field_edit(
    *,
    message: Message,
    registry: DatabaseRegistry,
    state: FSMContext,
    task_id: int,
    telegram_user_id: int,
) -> bool:
    """Show field-edit keyboard for an owned task. Returns False if missing."""
    task = await _owned_task(
        registry,
        task_id=task_id,
        telegram_user_id=telegram_user_id,
    )
    if not task:
        return False
    await state.set_state(TaskBrowse.browsing)
    await state.update_data(**{_SCREEN_MSG_KEY: message.message_id})
    with suppress(Exception):
        await message.edit_text(
            f"Edit *{escape_md(task.title)}* — what to change?",
            parse_mode="Markdown",
            reply_markup=my_task_edit_fields(task.id),
        )
        return True
    sent = await message.answer(
        f"Edit *{escape_md(task.title)}* — what to change?",
        parse_mode="Markdown",
        reply_markup=my_task_edit_fields(task.id),
    )
    await state.update_data(**{_SCREEN_MSG_KEY: sent.message_id})
    return True


@router.message(Command("tasks"))
async def cmd_tasks(
    message: Message,
    registry: DatabaseRegistry,
    state: FSMContext,
) -> None:
    """Open My tasks: sync this user's calendar queue, then the 7 closest pending."""
    await _show_list(message=message, registry=registry, state=state, edit=False)


@router.callback_query(F.data.startswith("mt:"))
async def handle_my_tasks_callback(
    callback: CallbackQuery,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not callback.data or not callback.message or not callback.from_user:
        return

    parts = callback.data.split(":")
    if len(parts) < 2:
        return

    action = parts[1]
    telegram_user_id = callback.from_user.id

    if action == "back":
        await callback.answer()
        await _show_list(
            message=callback.message,
            registry=registry,
            state=state,
            edit=True,
        )
        return

    if action == "main":
        await callback.answer()
        await _delete_screen(
            bot=callback.bot,
            chat_id=callback.message.chat.id,
            state=state,
        )
        await state.clear()
        from app.todobot.handlers.start import _send_welcome

        await _send_welcome(callback.message, registry, state)
        return

    if action == "done" and len(parts) >= 3:
        task_id = int(parts[2])
        task = await _owned_task(
            registry,
            task_id=task_id,
            telegram_user_id=telegram_user_id,
        )
        if not task:
            await callback.answer("Task not found.", show_alert=True)
            return
        await change_status(
            registry,
            task_id=task.id,
            new_status=TaskStatus.COMPLETED,
            actor_type=AuditActorType.TELEGRAM,
            actor_id=telegram_user_id,
            source=AuditSource.TODOBOT,
            allow_future_complete=True,
        )
        await callback.answer("Marked done.")
        await _show_list(
            message=callback.message,
            registry=registry,
            state=state,
            edit=True,
        )
        return

    if action == "o" and len(parts) >= 3:
        task_id = int(parts[2])
        task = await _owned_task(
            registry,
            task_id=task_id,
            telegram_user_id=telegram_user_id,
        )
        if not task:
            await callback.answer("Task not found.", show_alert=True)
            return
        await callback.answer()
        await _show_detail(callback=callback, task=task, state=state)
        return

    if action == "rm" and len(parts) >= 3:
        task_id = int(parts[2])
        task = await _owned_task(
            registry,
            task_id=task_id,
            telegram_user_id=telegram_user_id,
        )
        if not task:
            await callback.answer("Task not found.", show_alert=True)
            return
        await callback.answer()
        await callback.message.edit_text(
            f"Remove *{task.title}*?",
            parse_mode="Markdown",
            reply_markup=my_task_remove_choices(task.id),
        )
        return

    if action == "c" and len(parts) >= 4:
        task_id = int(parts[2])
        status_key = parts[3]
        new_status = _REMOVE_STATUS.get(status_key)
        if not new_status:
            return
        task = await _owned_task(
            registry,
            task_id=task_id,
            telegram_user_id=telegram_user_id,
        )
        if not task:
            await callback.answer("Task not found.", show_alert=True)
            return
        await change_status(
            registry,
            task_id=task.id,
            new_status=new_status,
            actor_type=AuditActorType.TELEGRAM,
            actor_id=telegram_user_id,
            source=AuditSource.TODOBOT,
        )
        await callback.answer(f"Marked as {new_status.value.replace('_', ' ')}.")
        await _show_list(
            message=callback.message,
            registry=registry,
            state=state,
            edit=True,
        )
        return

    if action == "e" and len(parts) >= 3:
        task_id = int(parts[2])
        ok = await open_task_field_edit(
            message=callback.message,
            registry=registry,
            state=state,
            task_id=task_id,
            telegram_user_id=telegram_user_id,
        )
        if not ok:
            await callback.answer("Task not found.", show_alert=True)
            return
        await callback.answer()
        return

    if action == "ew" and len(parts) >= 3:
        task_id = int(parts[2])
        task = await _owned_task(
            registry,
            task_id=task_id,
            telegram_user_id=telegram_user_id,
        )
        if not task:
            await callback.answer("Task not found.", show_alert=True)
            return
        await callback.answer()
        await state.set_state(TaskBrowse.editing_date)
        await state.update_data(**{_EDIT_TASK_KEY: task.id})
        await callback.message.edit_text(
            f"Pick a new date for *{escape_md(task.title)}*:",
            parse_mode="Markdown",
            reply_markup=my_task_date_picker(task.id),
        )
        return

    if action == "ef" and len(parts) >= 4:
        task_id = int(parts[2])
        field = parts[3]
        task = await _owned_task(
            registry,
            task_id=task_id,
            telegram_user_id=telegram_user_id,
        )
        if not task:
            await callback.answer("Task not found.", show_alert=True)
            return
        await callback.answer()
        await state.update_data(**{_EDIT_TASK_KEY: task.id})
        if field == "title":
            await state.set_state(TaskBrowse.editing_title)
            await callback.message.edit_text("Send the new title:")
        elif field == "location":
            await state.set_state(TaskBrowse.editing_location)
            await callback.message.edit_text("Send the new location:")
        elif field == "notes":
            await state.set_state(TaskBrowse.editing_notes)
            await callback.message.edit_text("Send the new notes:")
        return

    if action == "d" and len(parts) >= 4:
        task_id = int(parts[2])
        value = parts[3]
        task = await _owned_task(
            registry,
            task_id=task_id,
            telegram_user_id=telegram_user_id,
        )
        if not task:
            await callback.answer("Task not found.", show_alert=True)
            return
        await callback.answer()
        if value == "custom":
            await state.set_state(TaskBrowse.editing_date)
            await state.update_data(**{_EDIT_TASK_KEY: task.id})
            await callback.message.edit_text(
                "Send the date (e.g. tomorrow, 2026-11-01):",
            )
            return
        await state.set_state(TaskBrowse.editing_time)
        await state.update_data(
            **{_EDIT_TASK_KEY: task.id, _EDIT_DATE_KEY: value},
        )
        await callback.message.edit_text(
            f"Pick a time for *{task.title}* on {value}:",
            parse_mode="Markdown",
            reply_markup=my_task_time_picker(task.id, selected_date=value),
        )
        return

    if action == "t" and len(parts) >= 4:
        task_id = int(parts[2])
        value = parts[3]
        task = await _owned_task(
            registry,
            task_id=task_id,
            telegram_user_id=telegram_user_id,
        )
        if not task:
            await callback.answer("Task not found.", show_alert=True)
            return
        await callback.answer()
        data = await state.get_data()
        date_iso = data.get(_EDIT_DATE_KEY)
        if not date_iso:
            await callback.message.edit_text(
                "Pick a date first.",
                reply_markup=my_task_date_picker(task.id),
            )
            return
        if value == "custom":
            await state.set_state(TaskBrowse.editing_time)
            await state.update_data(**{_EDIT_TASK_KEY: task.id})
            await callback.message.edit_text("Send the time (e.g. 14:30 or 3pm):")
            return
        # value is HH-MM; block past times on today
        hhmm = value.replace("-", ":")
        now = local_now()
        if str(date_iso) == now.date().isoformat():
            hour, minute = map(int, hhmm.split(":"))
            if (hour, minute) <= (now.hour, now.minute):
                await callback.message.answer("That time is in the past. Pick another.")
                return
        scheduled_at = local_naive_to_utc(
            datetime.fromisoformat(f"{date_iso}T{hhmm}:00"),
        )
        task = await reschedule_task(
            registry,
            task_id=task.id,
            scheduled_at=scheduled_at,
            actor_type=AuditActorType.TELEGRAM,
            actor_id=telegram_user_id,
            source=AuditSource.TODOBOT,
        )
        await state.update_data(**{_EDIT_DATE_KEY: None, _EDIT_TASK_KEY: None})
        await _show_detail(callback=callback, task=task, state=state)
        return


@router.message(TaskBrowse.editing_title)
@router.message(TaskBrowse.editing_location)
@router.message(TaskBrowse.editing_notes)
async def handle_my_tasks_text_field(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not message.text or not message.from_user:
        await message.answer("Please send text.")
        return
    data = await state.get_data()
    task_id = data.get(_EDIT_TASK_KEY)
    if not task_id:
        await state.clear()
        await message.answer("Edit expired. Open My tasks again.")
        return
    task = await _owned_task(
        registry,
        task_id=int(task_id),
        telegram_user_id=message.from_user.id,
    )
    if not task:
        await state.clear()
        await message.answer("Task not found.")
        return

    current = await state.get_state()
    kwargs: dict[str, str] = {}
    if current == TaskBrowse.editing_title.state:
        kwargs["title"] = message.text.strip()
    elif current == TaskBrowse.editing_location.state:
        kwargs["location"] = message.text.strip()
    else:
        kwargs["description"] = message.text.strip()

    task = await update_task_details(
        registry,
        task_id=task.id,
        actor_type=AuditActorType.TELEGRAM,
        actor_id=message.from_user.id,
        source=AuditSource.TODOBOT,
        **kwargs,
    )
    await state.set_state(TaskBrowse.browsing)
    await state.update_data(**{_EDIT_TASK_KEY: None})
    await _delete_screen(bot=message.bot, chat_id=message.chat.id, state=state)
    sent = await message.answer(
        _detail_text(task),
        parse_mode="Markdown",
        reply_markup=my_task_detail(task.id),
    )
    await state.update_data(**{_SCREEN_MSG_KEY: sent.message_id})


@router.message(TaskBrowse.editing_date)
async def handle_my_tasks_date_text(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not message.text or not message.from_user:
        await message.answer("Please send a date.")
        return
    data = await state.get_data()
    task_id = data.get(_EDIT_TASK_KEY)
    if not task_id:
        await state.clear()
        await message.answer("Edit expired. Open My tasks again.")
        return
    task = await _owned_task(
        registry,
        task_id=int(task_id),
        telegram_user_id=message.from_user.id,
    )
    if not task:
        await state.clear()
        await message.answer("Task not found.")
        return
    parsed = parse_task_input(message.text)
    if not parsed.date:
        await message.answer("I couldn't understand that date. Try again:")
        return
    date_iso = parsed.date.isoformat()
    await state.set_state(TaskBrowse.editing_time)
    await state.update_data(**{_EDIT_DATE_KEY: date_iso})
    await _delete_screen(bot=message.bot, chat_id=message.chat.id, state=state)
    sent = await message.answer(
        f"Pick a time for *{task.title}* on {date_iso}:",
        parse_mode="Markdown",
        reply_markup=my_task_time_picker(task.id, selected_date=date_iso),
    )
    await state.update_data(**{_SCREEN_MSG_KEY: sent.message_id})


@router.message(TaskBrowse.editing_time)
async def handle_my_tasks_time_text(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not message.text or not message.from_user:
        await message.answer("Please send a time.")
        return
    data = await state.get_data()
    task_id = data.get(_EDIT_TASK_KEY)
    date_iso = data.get(_EDIT_DATE_KEY)
    if not task_id or not date_iso:
        await state.clear()
        await message.answer("Edit expired. Open My tasks again.")
        return
    task = await _owned_task(
        registry,
        task_id=int(task_id),
        telegram_user_id=message.from_user.id,
    )
    if not task:
        await state.clear()
        await message.answer("Task not found.")
        return

    parsed = parse_task_input(message.text)
    if parsed.time:
        hhmm = parsed.time.strftime("%H:%M")
    else:
        try:
            hhmm = datetime.strptime(message.text.strip(), "%H:%M").strftime("%H:%M")
        except ValueError:
            await message.answer("I couldn't understand that time. Try HH:MM:")
            return

    scheduled_at = local_naive_to_utc(
        datetime.fromisoformat(f"{date_iso}T{hhmm}:00"),
    )
    task = await reschedule_task(
        registry,
        task_id=task.id,
        scheduled_at=scheduled_at,
        actor_type=AuditActorType.TELEGRAM,
        actor_id=message.from_user.id,
        source=AuditSource.TODOBOT,
    )
    await state.update_data(**{_EDIT_DATE_KEY: None, _EDIT_TASK_KEY: None})
    await state.set_state(TaskBrowse.browsing)
    await _delete_screen(bot=message.bot, chat_id=message.chat.id, state=state)
    sent = await message.answer(
        _detail_text(task),
        parse_mode="Markdown",
        reply_markup=my_task_detail(task.id),
    )
    await state.update_data(**{_SCREEN_MSG_KEY: sent.message_id})


# Kept for any lingering status: callbacks from older messages.
_STATUS_MAP = {
    "completed": TaskStatus.COMPLETED,
    "not_completed": TaskStatus.NOT_COMPLETED,
    "postponed": TaskStatus.POSTPONED,
}


@router.callback_query(F.data.startswith("status:"))
async def handle_status_update(
    callback: CallbackQuery,
    registry: DatabaseRegistry,
) -> None:
    if not callback.data or not callback.message or not callback.from_user:
        return
    parts = callback.data.split(":")
    if len(parts) != 3:
        return

    task_id = int(parts[1])
    status_key = parts[2]
    new_status = _STATUS_MAP.get(status_key)
    if not new_status:
        return

    task = await _owned_task(
        registry,
        task_id=task_id,
        telegram_user_id=callback.from_user.id,
    )
    if not task:
        await callback.answer("Task not found.", show_alert=True)
        return

    try:
        task = await change_status(
            registry,
            task_id=task_id,
            new_status=new_status,
            actor_type=AuditActorType.TELEGRAM,
            actor_id=callback.from_user.id,
            source=AuditSource.TODOBOT,
        )
    except ConflictError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    await callback.answer()
    await callback.message.answer(
        f'Task "{task.title}" marked as {new_status.value}.',
    )
