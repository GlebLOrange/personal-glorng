/** Public slug for the weather tool and API. */
export const WEATHER_SLUG = "weather";

export const WEATHER_ROUTE_NAME = WEATHER_SLUG;

export const WEATHER_PATH = `/${WEATHER_SLUG}`;

export const WEATHER_API_PREFIX = `/${WEATHER_SLUG}`;

export const WEATHER_TOOL_NAME = "weather";

/** Legacy storage key prefix — kept so guest saved cities survive the rebrand. */
const LEGACY_SLUG = "time-date-weather-location";

export const SAVED_LOCATIONS_STORAGE_KEY = `${LEGACY_SLUG}:saved-locations`;

export const LEGACY_SAVED_LOCATIONS_STORAGE_KEY = "weather:saved-locations";

export const DEFAULT_WEATHER_LOCATION = {
  label: "Wrocław",
  query: "Wroclaw",
} as const;

/** Max saved cities for guests (localStorage) and authenticated users (server). */
export const MAX_SAVED_WEATHER_LOCATIONS = 8;

export const MAX_WEATHER_LOCATION_LABEL_LENGTH = 100;
export const MAX_WEATHER_LOCATION_QUERY_LENGTH = 100;
