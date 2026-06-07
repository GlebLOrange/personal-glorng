from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.telegram import TelegramInboundMessage
from app.db.mongo.counter import next_sequence_id


def _from_doc(data: dict[str, Any]) -> TelegramInboundMessage:
    payload = dict(data)
    payload.pop("_id", None)
    return TelegramInboundMessage(
        id=payload["id"],
        telegram_user_id=payload["telegram_user_id"],
        telegram_message_id=payload["telegram_message_id"],
        chat_id=payload["chat_id"],
        text=payload["text"],
        metadata_json=payload.get("metadata_json"),
        created_at=payload.get("created_at"),
    )


class TelegramRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db

    async def create(self, message: TelegramInboundMessage) -> TelegramInboundMessage:
        if not message.id:
            message.id = await next_sequence_id(self.db, "telegram_inbound_messages")
        await self.db.telegram_inbound_messages.insert_one(
            {
                "id": message.id,
                "telegram_user_id": message.telegram_user_id,
                "telegram_message_id": message.telegram_message_id,
                "chat_id": message.chat_id,
                "text": message.text,
                "metadata_json": message.metadata_json,
                "created_at": message.created_at,
            },
        )
        return message

    async def get(self, message_id: int) -> TelegramInboundMessage | None:
        data = await self.db.telegram_inbound_messages.find_one({"id": message_id})
        if data is None:
            return None
        return _from_doc(data)

    async def get_by_telegram_message_id(
        self,
        telegram_message_id: int,
    ) -> TelegramInboundMessage | None:
        data = await self.db.telegram_inbound_messages.find_one(
            {"telegram_message_id": telegram_message_id},
        )
        if data is None:
            return None
        return _from_doc(data)
