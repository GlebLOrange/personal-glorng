/** Public slug for the date, time, weather, and location section and API. */
export const TIME_DATE_WEATHER_LOCATION_SLUG = "time-date-weather-location";

export const TIME_DATE_WEATHER_LOCATION_ROUTE_NAME = TIME_DATE_WEATHER_LOCATION_SLUG;

export const TIME_DATE_WEATHER_LOCATION_PATH = `/${TIME_DATE_WEATHER_LOCATION_SLUG}`;

export const TIME_DATE_WEATHER_LOCATION_API_PREFIX = `/${TIME_DATE_WEATHER_LOCATION_SLUG}`;

export const DATE_TIME_LOCATION_SECTION = "date & time & location";

export const DEFAULT_WEATHER_LOCATION = {
  label: "Wrocław",
  query: "Wroclaw",
} as const;

export const SAVED_LOCATIONS_STORAGE_KEY = `${TIME_DATE_WEATHER_LOCATION_SLUG}:saved-locations`;

export const LEGACY_SAVED_LOCATIONS_STORAGE_KEY = "weather:saved-locations";
