from datetime import datetime
from typing import Any

from app.db.documents.base import utc_now


class TelegramInboundMessage:
    def __init__(
        self,
        *,
        id: int,
        telegram_user_id: int,
        telegram_message_id: int,
        chat_id: int,
        text: str,
        metadata_json: dict[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.telegram_user_id = telegram_user_id
        self.telegram_message_id = telegram_message_id
        self.chat_id = chat_id
        self.text = text
        self.metadata_json = metadata_json
        self.created_at = created_at or utc_now()
