from app.db.documents.base import TimestampedDocument


class Feedback(TimestampedDocument):
    email: str
    theme: str
    message: str
    status: str = "unread"
