"""Declarative MongoDB index definitions."""

from typing import Any

INDEX_SPECS: list[tuple[str, list[tuple[str, int]], dict[str, Any] | None]] = [
    ("users", [("email", 1)], {"unique": True}),
    ("users", [("public_id", 1)], {"unique": True}),
    ("tasks", [("telegram_user_id", 1), ("scheduled_at", 1)], None),
    ("tasks", [("status", 1)], None),
    ("task_status_history", [("task_id", 1), ("changed_at", 1)], None),
    ("reminders", [("task_id", 1)], None),
    ("reminders", [("sent", 1), ("remind_at", 1)], None),
    ("task_intakes", [("inbound_message_id", 1)], None),
    ("google_sync_queue", [("status", 1), ("created_at", 1)], None),
    ("shortened_urls", [("code", 1)], {"unique": True}),
    ("shared_files", [("code", 1)], {"unique": True}),
    ("github_credentials", [("user_id", 1)], {"unique": True}),
    ("google_credentials", [("telegram_user_id", 1)], {"unique": True}),
    ("telegram_inbound_messages", [("telegram_message_id", 1)], {"unique": True}),
    ("weather_locations", [("user_id", 1), ("query", 1)], {"unique": True}),
    ("tool_expense_categories", [("name", 1)], {"unique": True}),
    (
        "search_documents",
        [("title", "text"), ("body", "text")],
        {"name": "search_text_idx"},
    ),
    ("search_documents", [("source_type", 1), ("source_id", 1)], {"unique": True}),
    ("audit_events", [("occurred_at", -1)], None),
    ("audit_events", [("category", 1)], None),
    ("app_logs", [("occurred_at", -1)], None),
    ("app_logs", [("level", 1)], None),
    ("app_logs", [("service", 1)], None),
    ("app_logs", [("request_id", 1)], None),
]
