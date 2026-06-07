from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BaseModelMixin


class WeatherLocation(BaseModelMixin, Base):
    """User-saved weather location (city name or lat,lon coords)."""

    __tablename__ = "weather_locations"
    __table_args__ = (
        UniqueConstraint("user_id", "query", name="uq_weather_locations_user_query"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    label: Mapped[str] = mapped_column(String(100))
    query: Mapped[str] = mapped_column(String(100))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
