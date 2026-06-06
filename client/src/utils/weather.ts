import type { WeatherData } from "@/types";

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"] as const;
const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
] as const;

const CITY_PATTERN = /^[a-zA-Z\s\-'.]+$/;
const COORD_PATTERN = /^-?\d{1,3}(\.\d+)?,-?\d{1,3}(\.\d+)?$/;

/** Return true when query is a valid city name or lat,lon pair (matches server rules). */
export function isValidWeatherLocationQuery(location: string): boolean {
  const trimmed = location.trim();
  if (!trimmed) {
    return false;
  }
  return CITY_PATTERN.test(trimmed) || COORD_PATTERN.test(trimmed);
}

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

export interface LocalTimeParts {
  hours24: number;
  minutes: number;
  seconds: number;
}

/** Local Date for a UTC offset in hours (wall clock stored in UTC fields). */
export function localDateFromOffset(offsetHours: number): Date {
  const now = new Date();
  const utcMs = now.getTime() + now.getTimezoneOffset() * 60_000;
  return new Date(utcMs + offsetHours * 3_600_000);
}

/** Local time parts for a UTC offset in hours. */
export function localTimeFromOffset(offsetHours: number): LocalTimeParts {
  const local = localDateFromOffset(offsetHours);
  return {
    hours24: local.getUTCHours(),
    minutes: local.getUTCMinutes(),
    seconds: local.getUTCSeconds(),
  };
}

function pad2(value: number): string {
  return String(value).padStart(2, "0");
}

/** ISO-like datetime from offset clock (for time[datetime]). */
export function isoDateTimeFromOffset(offsetHours: number): string {
  const local = localDateFromOffset(offsetHours);
  return (
    `${local.getUTCFullYear()}-${pad2(local.getUTCMonth() + 1)}-${pad2(local.getUTCDate())}` +
    `T${pad2(local.getUTCHours())}:${pad2(local.getUTCMinutes())}:${pad2(local.getUTCSeconds())}`
  );
}

/** Live local time with seconds, e.g. "23:16:42". */
export function formatLiveLocalTimeWithSeconds(offsetHours: number): string {
  const { hours24, minutes, seconds } = localTimeFromOffset(offsetHours);
  return `${pad2(hours24)}:${pad2(minutes)}:${pad2(seconds)}`;
}

/** Live local time for a location using UTC offset from weather data. */
export function formatLiveLocalTime(offsetHours: number): string {
  const { hours24, minutes } = localTimeFromOffset(offsetHours);
  return `${pad2(hours24)}:${pad2(minutes)}`;
}

/** Live local date and time, e.g. "Sun Jun 7 12:55 am". */
export function formatLiveLocalDateTime(offsetHours: number): string {
  const local = localDateFromOffset(offsetHours);
  const weekday = WEEKDAYS[local.getUTCDay()];
  const month = MONTHS[local.getUTCMonth()];
  const day = local.getUTCDate();
  const hours24 = local.getUTCHours();
  const minutes = local.getUTCMinutes();
  const ampm = hours24 >= 12 ? "pm" : "am";
  const hour12 = hours24 % 12 || 12;
  return `${weekday} ${month} ${day} ${hour12}:${pad2(minutes)} ${ampm}`;
}
