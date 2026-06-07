"""CRUD for user-saved weather locations."""

from app.core.exceptions import ApiError, ValidationError
from app.db.documents.weather import WeatherLocation
from app.db.registry import DatabaseRegistry
from app.services.weather import is_valid_location
from app.settings import get_settings

MAX_LOCATIONS_PER_USER = 8


def _weather(registry: DatabaseRegistry):
    if registry.weather is None:
        msg = "Weather repository is not initialized"
        raise RuntimeError(msg)
    return registry.weather


def _is_default_query(query: str) -> bool:
    settings = get_settings()
    return query.strip().lower() == settings.WEATHER_DEFAULT_QUERY.lower()


class WeatherLocationService:
    def __init__(self, registry: DatabaseRegistry) -> None:
        self.registry = registry

    async def list_locations(self, user_id: int) -> list[WeatherLocation]:
        return await _weather(self.registry).list_for_user(user_id)

    async def add_location(
        self,
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

        existing = await self.list_locations(user_id)
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
        return await _weather(self.registry).insert(location)

    async def remove_location(self, user_id: int, location_id: int) -> None:
        location = await self._get_owned_location(user_id, location_id)
        if _is_default_query(location.query):
            raise ValidationError("Default location cannot be removed")
        await _weather(self.registry).delete(location_id)

    async def reorder_locations(
        self,
        user_id: int,
        ordered_ids: list[int],
    ) -> list[WeatherLocation]:
        locations = await self.list_locations(user_id)
        owned_ids = {loc.id for loc in locations}
        if set(ordered_ids) != owned_ids:
            raise ValidationError("Ordered ids must match saved locations")

        order_map = {
            location_id: index for index, location_id in enumerate(ordered_ids)
        }
        for location in locations:
            await _weather(self.registry).update_fields(
                location.id,
                sort_order=order_map[location.id],
            )
        return await self.list_locations(user_id)

    async def _get_owned_location(
        self,
        user_id: int,
        location_id: int,
    ) -> WeatherLocation:
        location = await _weather(self.registry).get_or_none(location_id)
        if not location or location.user_id != user_id:
            raise ApiError(404, "Location not found")
        return location
