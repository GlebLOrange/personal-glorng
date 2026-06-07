from datetime import datetime

from app.db.documents.base import TimestampedDocument, utc_now


class GitHubCredential(TimestampedDocument):
    user_id: int
    github_user_id: int
    github_username: str
    access_token: str


class GoogleCredential:
    def __init__(
        self,
        *,
        id: int,
        telegram_user_id: int,
        refresh_token: str,
        calendar_id: str = "primary",
        sync_token: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.telegram_user_id = telegram_user_id
        self.refresh_token = refresh_token
        self.calendar_id = calendar_id
        self.sync_token = sync_token
        self.created_at = created_at or utc_now()
        self.updated_at = updated_at or utc_now()
