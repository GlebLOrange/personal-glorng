"""Celery / RabbitMQ queue declarations and dead-letter publishing."""

from typing import Any

from kombu import Exchange, Queue

from app.core.logging import logger

CELERY_QUEUE_NAME = "celery"
CELERY_DLQ_NAME = "celery.dlq"
CELERY_DLX_NAME = "celery.dlx"

celery_exchange = Exchange("celery", type="direct", durable=True)
celery_dlx = Exchange(CELERY_DLX_NAME, type="direct", durable=True)

celery_queue = Queue(
    CELERY_QUEUE_NAME,
    exchange=celery_exchange,
    routing_key=CELERY_QUEUE_NAME,
    durable=True,
    queue_arguments={
        "x-dead-letter-exchange": CELERY_DLX_NAME,
        "x-dead-letter-routing-key": CELERY_DLQ_NAME,
    },
)

celery_dlq = Queue(
    CELERY_DLQ_NAME,
    exchange=celery_dlx,
    routing_key=CELERY_DLQ_NAME,
    durable=True,
)


def publish_dead_letter(
    *,
    task_name: str,
    task_id: str | None,
    args: tuple[Any, ...] | list[Any] | None,
    kwargs: dict[str, Any] | None,
    retries: int,
    exc: BaseException,
) -> None:
    """Persist a failed task payload on the DLQ (workers do not consume it)."""
    from app.workers.celery_app import celery_app

    payload = {
        "task": task_name,
        "id": task_id,
        "args": list(args or ()),
        "kwargs": dict(kwargs or {}),
        "retries": retries,
        "exception": f"{type(exc).__name__}: {exc}",
    }
    if celery_app.conf.task_always_eager:
        logger.warning(
            "Dead-letter skipped in eager mode",
            context={
                "task_name": task_name,
                "task_id": task_id,
                "exception": payload["exception"],
            },
        )
        return
    try:
        with celery_app.producer_pool.acquire(block=True) as producer:
            producer.publish(
                payload,
                exchange=celery_dlx,
                routing_key=CELERY_DLQ_NAME,
                serializer="json",
                delivery_mode=2,
                declare=[celery_dlx, celery_dlq],
            )
        logger.warning(
            "Published task to dead-letter queue",
            context={
                "task_name": task_name,
                "task_id": task_id,
                "queue": CELERY_DLQ_NAME,
            },
        )
    except Exception as publish_exc:
        logger.error(
            "Failed to publish task to dead-letter queue",
            error=publish_exc,
            context={"task_name": task_name, "task_id": task_id},
        )
