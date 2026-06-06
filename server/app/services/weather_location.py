"""CRUD for user-saved weather locations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApiError, ValidationError
from app.db.models.weather_location import WeatherLocation
from app.services.weather import is_valid_location

MAX_LOCATIONS_PER_USER = 8


class WeatherLocationService:
    async def list_locations(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[WeatherLocation]:
        result = await db.execute(
            select(WeatherLocation)
            .where(WeatherLocation.user_id == user_id)
            .order_by(WeatherLocation.sort_order, WeatherLocation.id)
        )
        return list(result.scalars().all())

    async def add_location(
        self,
        db: AsyncSession,
        user_id: int,
        *,
        label: str,
        query: str,
    ) -> WeatherLocation:
        trimmed_query = query.strip()
        trimmed_label = label.strip() or trimmed_query
        if not is_valid_location(trimmed_query):
            raise ValidationError("Location contains invalid characters")
        if not trimmed_label:
            raise ValidationError("Label is required")

        existing = await self.list_locations(db, user_id)
        if any(loc.query.lower() == trimmed_query.lower() for loc in existing):
            raise ValidationError("Location already saved")
        if len(existing) >= MAX_LOCATIONS_PER_USER:
            raise ApiError(400, f"Maximum {MAX_LOCATIONS_PER_USER} locations allowed")

        location = WeatherLocation(
            user_id=user_id,
            label=trimmed_label,
            query=trimmed_query,
            sort_order=len(existing),
        )
        db.add(location)
        await db.commit()
        await db.refresh(location)
        return location

    async def remove_location(
        self,
        db: AsyncSession,
        user_id: int,
        location_id: int,
    ) -> None:
        location = await self._get_owned_location(db, user_id, location_id)
        await db.delete(location)
        await db.commit()

    async def reorder_locations(
        self,
        db: AsyncSession,
        user_id: int,
        ordered_ids: list[int],
    ) -> list[WeatherLocation]:
        locations = await self.list_locations(db, user_id)
        owned_ids = {loc.id for loc in locations}
        if set(ordered_ids) != owned_ids:
            raise ValidationError("Ordered ids must match saved locations")

        order_map = {
            location_id: index for index, location_id in enumerate(ordered_ids)
        }
        for location in locations:
            location.sort_order = order_map[location.id]
        await db.commit()
        return await self.list_locations(db, user_id)

    async def _get_owned_location(
        self,
        db: AsyncSession,
        user_id: int,
        location_id: int,
    ) -> WeatherLocation:
        result = await db.execute(
            select(WeatherLocation).where(
                WeatherLocation.id == location_id,
                WeatherLocation.user_id == user_id,
            )
        )
        location = result.scalar_one_or_none()
        if not location:
            raise ApiError(404, "Location not found")
        return location
