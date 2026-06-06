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

export interface LocalTimeParts {
  hours24: number;
  minutes: number;
  seconds: number;
}

export interface ClockHandAngles {
  hour: number;
  minute: number;
  second: number;
}

/** Local Date for a UTC offset in hours. */
export function localDateFromOffset(offsetHours: number): Date {
  const now = new Date();
  const utcMs = now.getTime() + now.getTimezoneOffset() * 60_000;
  return new Date(utcMs + offsetHours * 3_600_000);
}

/** Local time parts for a UTC offset in hours. */
export function localTimeFromOffset(offsetHours: number): LocalTimeParts {
  const local = localDateFromOffset(offsetHours);
  return {
    hours24: local.getHours(),
    minutes: local.getMinutes(),
    seconds: local.getSeconds(),
  };
}

/** Analog clock hand angles in degrees (0 = 12 o'clock, clockwise). */
export function clockHandAngles(parts: LocalTimeParts): ClockHandAngles {
  const hour12 = parts.hours24 % 12;
  return {
    hour: hour12 * 30 + parts.minutes * 0.5,
    minute: parts.minutes * 6,
    second: parts.seconds * 6,
  };
}

/** Live local time for a location using UTC offset from weather data. */
export function formatLiveLocalTime(offsetHours: number): string {
  const { hours24, minutes } = localTimeFromOffset(offsetHours);
  return `${String(hours24).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
}

/** Live local date and time, e.g. "Sun Jun 7 12:55 am". */
export function formatLiveLocalDateTime(offsetHours: number): string {
  const local = localDateFromOffset(offsetHours);
  const weekday = local.toLocaleDateString("en-US", { weekday: "short" });
  const month = local.toLocaleDateString("en-US", { month: "short" });
  const day = local.getDate();
  const time = local
    .toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true })
    .toLowerCase();
  return `${weekday} ${month} ${day} ${time}`;
}
