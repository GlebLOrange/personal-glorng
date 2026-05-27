"""Task listing, status updates, and deletion."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import TaskStatus
from app.services.task import get_pending_tasks, get_task, update_task_status

router = Router()


@router.message(Command("tasks"))
async def cmd_tasks(message: Message, db: AsyncSession) -> None:
    if not message.from_user:
        return

    tasks = await get_pending_tasks(
        db,
        telegram_user_id=message.from_user.id,
    )
    if not tasks:
        await message.answer("No pending tasks. Use /new to create one!")
        return

    lines = ["*Your pending tasks:*\n"]
    for i, task in enumerate(tasks, 1):
        scheduled = task.scheduled_at[:16] if task.scheduled_at else "—"
        loc = f" ({task.location})" if task.location else ""
        lines.append(f"{i}. {task.title} — {scheduled}{loc}")

    await message.answer("\n".join(lines), parse_mode="Markdown")


_STATUS_MAP = {
    "completed": TaskStatus.COMPLETED,
    "not_completed": TaskStatus.NOT_COMPLETED,
    "postponed": TaskStatus.POSTPONED,
}


@router.callback_query(F.data.startswith("status:"))
async def handle_status_update(
    callback: CallbackQuery,
    db: AsyncSession,
) -> None:
    if not callback.data or not callback.message:
        return
    parts = callback.data.split(":")
    if len(parts) != 3:
        return

    task_id = int(parts[1])
    status_key = parts[2]
    new_status = _STATUS_MAP.get(status_key)
    if not new_status:
        return

    await callback.answer()

    task = await get_task(db, task_id=task_id)
    if not task:
        await callback.message.answer("Task not found.")
        return

    await update_task_status(db, task=task, new_status=new_status)
    await callback.message.answer(
        f'Task "{task.title}" marked as {new_status.value}.',
    )
