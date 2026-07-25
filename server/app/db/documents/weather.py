from app.db.documents.base import TimestampedDocument


class WeatherLocation(TimestampedDocument):
    user_id: int
    query: str
    sort_order: int = 0
