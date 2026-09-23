"""Celery beat schedule registry (P2 unit — no live beat firing)."""

from celery.schedules import crontab

from app.workers.celery_app import celery_app
from app.workers.job_names import JobName


def test_beat_schedule_entries_resolve() -> None:
    schedule = celery_app.conf.beat_schedule
    assert "check-overdue-tasks" in schedule
    assert schedule["check-overdue-tasks"]["task"] == JobName.CHECK_OVERDUE_TASKS
    assert isinstance(schedule["check-overdue-tasks"]["schedule"], crontab)

    assert schedule["cleanup-old-tasks"]["task"] == JobName.CLEANUP_OLD_TASKS
    assert schedule["cleanup-expired-shares"]["task"] == JobName.CLEANUP_EXPIRED_SHARES
    assert schedule["process-sync-queue"]["task"] == JobName.PROCESS_SYNC_QUEUE
    assert schedule["run-health-checks"]["task"] == JobName.RUN_HEALTH_CHECKS
    assert isinstance(schedule["run-health-checks"]["schedule"], crontab)
    assert schedule["cleanup-health-results"]["task"] == JobName.CLEANUP_HEALTH_RESULTS
