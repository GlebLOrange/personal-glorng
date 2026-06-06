import type { WeatherData } from "@/types";

/** Resolved location label from wttr.in payload. */
export function weatherLocationLabel(data: WeatherData): string {
  const area = data.nearest_area?.[0];
  const name = area?.areaName?.[0]?.value;
  const country = area?.country?.[0]?.value;
  if (name && country) {
    return `${name}, ${country}`;
  }
  return name ?? country ?? "Unknown location";
}

/** UTC offset in hours from wttr.in payload. */
export function weatherUtcOffsetHours(data: WeatherData): number | null {
  const offset = data.time_zone?.[0]?.utcOffset;
  if (!offset) {
    return null;
  }
  const parsed = Number.parseFloat(offset);
  return Number.isFinite(parsed) ? parsed : null;
}

/** Static local time string from wttr observation timestamp. */
export function weatherObservedTime(data: WeatherData): string | null {
  const obs = data.current_condition?.[0]?.localObsDateTime;
  if (!obs) {
    return null;
  }
  const parts = obs.split(" ");
  if (parts.length >= 3) {
    return `${parts[1]} ${parts[2]}`;
  }
  return obs;
}

/** Live local time for a location using UTC offset from weather data. */
export function formatLiveLocalTime(offsetHours: number): string {
  const now = new Date();
  const utcMs = now.getTime() + now.getTimezoneOffset() * 60_000;
  const local = new Date(utcMs + offsetHours * 3_600_000);
  return local.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}
