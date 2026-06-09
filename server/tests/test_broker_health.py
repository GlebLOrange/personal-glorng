"""RabbitMQ broker connectivity checks."""

from unittest.mock import MagicMock, patch

from app.workers.broker_health import check_broker_connection


def test_broker_connection_fails_when_broker_raises() -> None:
    connection = MagicMock()
    connection.ensure_connection.side_effect = ConnectionError("broker down")
    manager = MagicMock()
    manager.__enter__.return_value = connection
    manager.__exit__.return_value = None

    with patch(
        "app.workers.celery_app.celery_app.connection_or_acquire",
        return_value=manager,
    ):
        assert check_broker_connection() is False


def test_broker_connection_succeeds_when_broker_accepts() -> None:
    connection = MagicMock()
    manager = MagicMock()
    manager.__enter__.return_value = connection
    manager.__exit__.return_value = None

    with patch(
        "app.workers.celery_app.celery_app.connection_or_acquire",
        return_value=manager,
    ):
        assert check_broker_connection() is True
