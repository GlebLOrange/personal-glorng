"""Registered background job identifiers."""

from enum import StrEnum


class JobName(StrEnum):
    SEND_VERIFICATION_EMAIL = "send_verification_email"
    SEND_RESET_EMAIL = "send_reset_email"
    SEND_REMINDER = "send_reminder"
    CHECK_OVERDUE_TASKS = "check_overdue_tasks"
    CLEANUP_OLD_TASKS = "cleanup_old_tasks"
    CLEANUP_EXPIRED_SHARES = "cleanup_expired_shares"
    PROCESS_SYNC_QUEUE = "process_sync_queue"
    INGEST_NEWS = "ingest_news"
    PUBLISH_NEWS_TELEGRAM = "publish_news_telegram"
