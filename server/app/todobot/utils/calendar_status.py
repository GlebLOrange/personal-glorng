"""Post-create Google Calendar status lines for Telegram replies."""

from app.db.documents.task import Task
from app.db.registry import DatabaseRegistry

LINE_NOT_LINKED = "📅 Calendar not linked — /connect_calendar to sync events."
LINE_ADDED = "📅 Added to Google Calendar."
LINE_PENDING = "📅 Calendar sync pending — open Calendar → Sync now."


async def calendar_post_create_line(
    registry: DatabaseRegistry,
    *,
    telegram_user_id: int,
    task: Task,
) -> str:
    """Status after ``create_with_sync`` drain: linked+synced, pending, or unlinked.

    Reloads the task so ``google_event_id`` written by the sync worker is visible.
    """
    fresh = task
    if registry.tasks is not None:
        reloaded = await registry.tasks.get_or_none(task.id)
        if reloaded is not None:
            fresh = reloaded

    if registry.credentials is None:
        return LINE_NOT_LINKED
    cred = await registry.credentials.get_google_for_telegram_user(telegram_user_id)
    if cred is None:
        return LINE_NOT_LINKED
    if fresh.google_event_id:
        return LINE_ADDED
    return LINE_PENDING
