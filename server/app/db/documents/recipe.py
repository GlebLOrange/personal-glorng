from app.db.documents.base import TimestampedDocument


class Recipe(TimestampedDocument):
    title: str
    ingredients: str
    steps: str
    notes: str | None = None
    tags: str = "[]"
    image_url: str | None = None
    prep_time: int | None = None
    cook_time: int | None = None
    servings: int | None = None
