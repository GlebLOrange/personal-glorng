import {
  MAX_SAVED_WEATHER_LOCATIONS,
  MAX_WEATHER_LOCATION_QUERY_LENGTH,
} from "@/constants/weather";
import { isValidWeatherLocationQuery } from "@/utils/weather";

export interface GuestWeatherLocation {
  id: string;
  query: string;
  sort_order: number;
  is_default?: boolean;
}

function trimField(value: unknown, maxLength: number): string {
  if (typeof value !== "string") {
    return "";
  }
  return value.trim().slice(0, maxLength);
}

function isGuestLocation(value: unknown): value is GuestWeatherLocation {
  if (!value || typeof value !== "object") {
    return false;
  }
  const record = value as Record<string, unknown>;
  return typeof record.id === "string" && typeof record.query === "string";
}

/** Validate and cap guest locations loaded from localStorage. */
export function sanitizeGuestWeatherLocations(raw: unknown): GuestWeatherLocation[] {
  if (!Array.isArray(raw)) {
    return [];
  }

  const seen = new Set<string>();
  const sanitized: GuestWeatherLocation[] = [];

  for (const item of raw) {
    if (sanitized.length >= MAX_SAVED_WEATHER_LOCATIONS) {
      break;
    }
    if (!isGuestLocation(item)) {
      continue;
    }

    const query = trimField(item.query, MAX_WEATHER_LOCATION_QUERY_LENGTH);
    if (!isValidWeatherLocationQuery(query)) {
      continue;
    }

    const normalizedQuery = query.toLowerCase();
    if (seen.has(normalizedQuery)) {
      continue;
    }
    seen.add(normalizedQuery);

    sanitized.push({
      id: item.id,
      query,
      sort_order: sanitized.length,
      ...(item.is_default === true ? { is_default: true } : {}),
    });
  }

  return sanitized;
}

export function guestLocationLimitMessage(currentCount: number): string {
  return `${currentCount}/${MAX_SAVED_WEATHER_LOCATIONS} locations saved in your browser`;
}
