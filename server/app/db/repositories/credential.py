from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.credential import GitHubCredential, GoogleCredential
from app.db.documents.base import document_to_dict, utc_now
from app.db.mongo.counter import next_sequence_id
from app.db.repositories.base import MongoRepository, _parse_doc


def _google_from_doc(data: dict[str, Any]) -> GoogleCredential:
    payload = dict(data)
    payload.pop("_id", None)
    return GoogleCredential(
        id=payload["id"],
        telegram_user_id=payload["telegram_user_id"],
        refresh_token=payload["refresh_token"],
        calendar_id=payload.get("calendar_id", "primary"),
        sync_token=payload.get("sync_token"),
        created_at=payload.get("created_at"),
        updated_at=payload.get("updated_at"),
    )


class CredentialRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.github = MongoRepository(db, "github_credentials", GitHubCredential)

    async def get_github_for_user(self, user_id: int) -> GitHubCredential | None:
        data = await self.db.github_credentials.find_one({"user_id": user_id})
        if data is None:
            return None
        return _parse_doc(GitHubCredential, data)

    async def delete_github_for_user(self, user_id: int) -> None:
        await self.db.github_credentials.delete_one({"user_id": user_id})

    async def upsert_github(self, cred: GitHubCredential) -> GitHubCredential:
        cred.updated_at = utc_now()
        if not cred.id:
            cred.id = await next_sequence_id(self.db, "github_credentials")
            cred.created_at = utc_now()
            await self.db.github_credentials.insert_one(document_to_dict(cred))
            return cred
        await self.db.github_credentials.replace_one(
            {"user_id": cred.user_id},
            document_to_dict(cred),
            upsert=True,
        )
        return cred

    async def get_google_for_telegram_user(
        self,
        telegram_user_id: int,
    ) -> GoogleCredential | None:
        data = await self.db.google_credentials.find_one(
            {"telegram_user_id": telegram_user_id},
        )
        if data is None:
            return None
        return _google_from_doc(data)

    async def upsert_google(self, cred: GoogleCredential) -> GoogleCredential:
        cred.updated_at = utc_now()
        if not cred.id:
            cred.id = await next_sequence_id(self.db, "google_credentials")
            cred.created_at = utc_now()
        await self.db.google_credentials.replace_one(
            {"telegram_user_id": cred.telegram_user_id},
            {
                "id": cred.id,
                "telegram_user_id": cred.telegram_user_id,
                "refresh_token": cred.refresh_token,
                "calendar_id": cred.calendar_id,
                "sync_token": cred.sync_token,
                "created_at": cred.created_at,
                "updated_at": cred.updated_at,
            },
            upsert=True,
        )
        return cred

    async def delete_google_for_telegram_user(self, telegram_user_id: int) -> None:
        await self.db.google_credentials.delete_one(
            {"telegram_user_id": telegram_user_id},
        )
