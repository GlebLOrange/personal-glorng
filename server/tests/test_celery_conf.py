"""Celery reliability config (acks, timeouts, durable queues, DLQ)."""

from kombu import Queue

from app.workers.celery_app import celery_app
from app.workers.queues import (
    CELERY_DLQ_NAME,
    CELERY_QUEUE_NAME,
    celery_dlq,
    celery_queue,
    redact_task_payload,
)
from app.workers.tasks import MAX_JOB_TRIES, _retry_countdown


def test_celery_reliability_conf() -> None:
    conf = celery_app.conf
    assert conf.task_acks_late is True
    assert conf.task_reject_on_worker_lost is True
    assert conf.task_acks_on_failure_or_timeout is True
    assert conf.worker_prefetch_multiplier == 1
    assert conf.task_soft_time_limit == 300
    assert conf.task_time_limit == 360
    assert conf.task_default_delivery_mode == 2
    assert conf.task_default_queue == CELERY_QUEUE_NAME
    assert conf.result_backend is None
    assert conf.task_ignore_result is True


def test_celery_default_queue_is_durable_with_dlx() -> None:
    queues = celery_app.conf.task_queues
    assert queues is not None
    named = {q.name: q for q in queues if isinstance(q, Queue)}
    assert CELERY_QUEUE_NAME in named
    assert CELERY_DLQ_NAME not in named  # workers must not consume the DLQ
    q = named[CELERY_QUEUE_NAME]
    assert q.durable is True
    assert q.queue_arguments == {
        "x-dead-letter-exchange": "celery.dlx",
        "x-dead-letter-routing-key": CELERY_DLQ_NAME,
    }
    assert celery_queue.durable is True
    assert celery_dlq.durable is True
    assert celery_dlq.name == CELERY_DLQ_NAME


def test_retry_countdown_is_exponential_and_capped() -> None:
    assert MAX_JOB_TRIES == 3
    first = _retry_countdown(1)
    second = _retry_countdown(2)
    # 2^1*30=60 .. 75; 2^2*30=120 .. 135
    assert 60 <= first <= 75
    assert 120 <= second <= 135
    huge = _retry_countdown(10)
    assert 600 <= huge <= 615


def test_dlq_payload_redacts_jwt_tokens() -> None:
    jwt = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIn0."
        "signaturepaddingvaluehereXXXX"
    )
    args, kwargs = redact_task_payload(
        ("user@example.com", jwt),
        {"token": jwt, "reminder_id": 7},
    )
    assert args[0] == "user@example.com"
    assert args[1] == "[redacted]"
    assert kwargs["token"] == "[redacted]"
    assert kwargs["reminder_id"] == 7
