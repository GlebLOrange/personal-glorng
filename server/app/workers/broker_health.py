"""RabbitMQ broker connectivity checks."""


def check_broker_connection() -> bool:
    """Return True when the Celery broker accepts a connection."""
    from app.workers.celery_app import celery_app

    try:
        with celery_app.connection_or_acquire() as conn:
            conn.ensure_connection(max_retries=1, timeout=2)
    except Exception:
        return False
    return True
