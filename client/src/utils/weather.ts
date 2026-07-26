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

function parseUtcOffsetHours(value: string): number | null {
  if (value.includes(":")) {
    const sign = value.startsWith("-") ? -1 : 1;
    const cleaned = value.replace(/^[+-]/, "");
    const [hoursPart, minutesPart = "0"] = cleaned.split(":");
    const hours = Number.parseInt(hoursPart, 10);
    const minutes = Number.parseInt(minutesPart, 10);
    if (!Number.isFinite(hours) || !Number.isFinite(minutes)) {
      return null;
    }
    return sign * (hours + minutes / 60);
  }
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : null;
}

/** UTC offset in hours from weather payload. */
export function weatherUtcOffsetHours(data: WeatherData): number | null {
  const offset = data.time_zone?.[0]?.utcOffset;
  if (!offset) {
    return null;
  }
  return parseUtcOffsetHours(offset);
}

/** Unix time anchor from enriched weather payload. */
export function weatherAnchorUnixtime(data: WeatherData): number | null {
  const unixtime = data.time_zone?.[0]?.unixtime;
  if (typeof unixtime !== "number" || !Number.isFinite(unixtime)) {
    return null;
  }
  return unixtime;
}

/** IANA timezone id from enriched weather payload (e.g. Europe/Warsaw). */
export function weatherIanaTimezone(data: WeatherData): string | null {
  const timezone = data.time_zone?.[0]?.timezone?.trim();
  if (!timezone || !timezone.includes("/")) {
    return null;
  }
  return timezone;
}

export type LiveTimeFormatKind = "time" | "time-seconds" | "datetime" | "date";

function intlParts(
  date: Date,
  timezone: string,
  options: Intl.DateTimeFormatOptions,
): Intl.DateTimeFormatPart[] {
  return new Intl.DateTimeFormat("en-US", { timeZone: timezone, ...options }).formatToParts(date);
}

function partValue(parts: Intl.DateTimeFormatPart[], type: Intl.DateTimeFormatPartTypes): string {
  return parts.find((part) => part.type === type)?.value ?? "";
}

/** Live local time via IANA timezone (DST-safe). */
export function formatLiveLocalTimeFromIana(timezone: string, at: Date = new Date()): string {
  const parts = intlParts(at, timezone, {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  return `${partValue(parts, "hour")}:${partValue(parts, "minute")}`;
}

export function formatLiveLocalTimeWithSecondsFromIana(
  timezone: string,
  at: Date = new Date(),
): string {
  const parts = intlParts(at, timezone, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
  return `${partValue(parts, "hour")}:${partValue(parts, "minute")}:${partValue(parts, "second")}`;
}

export function formatLiveLocalDateFromIana(timezone: string, at: Date = new Date()): string {
  const parts = intlParts(at, timezone, {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
  return `${partValue(parts, "weekday")}, ${partValue(parts, "month")} ${partValue(parts, "day")}`;
}

export function formatLiveLocalDateTimeFromIana(timezone: string, at: Date = new Date()): string {
  const parts = intlParts(at, timezone, {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
  const weekday = partValue(parts, "weekday");
  const month = partValue(parts, "month");
  const day = partValue(parts, "day");
  const hour = partValue(parts, "hour");
  const minute = partValue(parts, "minute");
  const dayPeriod = partValue(parts, "dayPeriod").toLowerCase();
  return `${weekday} ${month} ${day} ${hour}:${minute} ${dayPeriod}`;
}

export function isoDateTimeFromIana(timezone: string, at: Date = new Date()): string {
  const parts = intlParts(at, timezone, {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
  return (
    `${partValue(parts, "year")}-${partValue(parts, "month")}-${partValue(parts, "day")}` +
    `T${partValue(parts, "hour")}:${partValue(parts, "minute")}:${partValue(parts, "second")}`
  );
}

export function isoDateFromIana(timezone: string, at: Date = new Date()): string {
  const parts = intlParts(at, timezone, {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  return `${partValue(parts, "year")}-${partValue(parts, "month")}-${partValue(parts, "day")}`;
}

export function formatLiveLocalFromIana(
  timezone: string,
  format: LiveTimeFormatKind,
  at: Date = new Date(),
): string {
  if (format === "datetime") {
    return formatLiveLocalDateTimeFromIana(timezone, at);
  }
  if (format === "time-seconds") {
    return formatLiveLocalTimeWithSecondsFromIana(timezone, at);
  }
  if (format === "date") {
    return formatLiveLocalDateFromIana(timezone, at);
  }
  return formatLiveLocalTimeFromIana(timezone, at);
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

/** Local time parts from a unix anchor and UTC offset in hours. */
export function localTimePartsFromUnix(unixtime: number, offsetHours: number): LocalTimeParts {
  const local = new Date(unixtime * 1000 + offsetHours * 3_600_000);
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

/** ISO-like datetime from unix anchor and offset. */
export function isoDateTimeFromUnix(unixtime: number, offsetHours: number): string {
  const { hours24, minutes, seconds } = localTimePartsFromUnix(unixtime, offsetHours);
  const local = new Date(unixtime * 1000 + offsetHours * 3_600_000);
  return (
    `${local.getUTCFullYear()}-${pad2(local.getUTCMonth() + 1)}-${pad2(local.getUTCDate())}` +
    `T${pad2(hours24)}:${pad2(minutes)}:${pad2(seconds)}`
  );
}

/** Live local time with seconds, e.g. "23:16:42". */
export function formatLiveLocalTimeWithSeconds(offsetHours: number): string {
  const { hours24, minutes, seconds } = localTimeFromOffset(offsetHours);
  return `${pad2(hours24)}:${pad2(minutes)}:${pad2(seconds)}`;
}

export function formatLiveLocalTimeWithSecondsFromUnix(
  unixtime: number,
  offsetHours: number,
): string {
  const { hours24, minutes, seconds } = localTimePartsFromUnix(unixtime, offsetHours);
  return `${pad2(hours24)}:${pad2(minutes)}:${pad2(seconds)}`;
}

/** Live local time for a location using UTC offset from weather data. */
export function formatLiveLocalTime(offsetHours: number): string {
  const { hours24, minutes } = localTimeFromOffset(offsetHours);
  return `${pad2(hours24)}:${pad2(minutes)}`;
}

export function formatLiveLocalTimeFromUnix(unixtime: number, offsetHours: number): string {
  const { hours24, minutes } = localTimePartsFromUnix(unixtime, offsetHours);
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

export function formatLiveLocalDateTimeFromUnix(unixtime: number, offsetHours: number): string {
  const local = new Date(unixtime * 1000 + offsetHours * 3_600_000);
  const weekday = WEEKDAYS[local.getUTCDay()];
  const month = MONTHS[local.getUTCMonth()];
  const day = local.getUTCDate();
  const hours24 = local.getUTCHours();
  const minutes = local.getUTCMinutes();
  const ampm = hours24 >= 12 ? "pm" : "am";
  const hour12 = hours24 % 12 || 12;
  return `${weekday} ${month} ${day} ${hour12}:${pad2(minutes)} ${ampm}`;
}

/** Live local date only, e.g. "Sun, Jun 7". */
export function formatLiveLocalDate(offsetHours: number): string {
  const local = localDateFromOffset(offsetHours);
  return `${WEEKDAYS[local.getUTCDay()]}, ${MONTHS[local.getUTCMonth()]} ${local.getUTCDate()}`;
}

export function formatLiveLocalDateFromUnix(unixtime: number, offsetHours: number): string {
  const local = new Date(unixtime * 1000 + offsetHours * 3_600_000);
  return `${WEEKDAYS[local.getUTCDay()]}, ${MONTHS[local.getUTCMonth()]} ${local.getUTCDate()}`;
}

/** ISO date from offset clock (for date-only time[datetime]). */
export function isoDateFromOffset(offsetHours: number): string {
  const local = localDateFromOffset(offsetHours);
  return `${local.getUTCFullYear()}-${pad2(local.getUTCMonth() + 1)}-${pad2(local.getUTCDate())}`;
}

/** ISO date from unix anchor and offset. */
export function isoDateFromUnix(unixtime: number, offsetHours: number): string {
  const local = new Date(unixtime * 1000 + offsetHours * 3_600_000);
  return `${local.getUTCFullYear()}-${pad2(local.getUTCMonth() + 1)}-${pad2(local.getUTCDate())}`;
}

export type WeatherConditionKind =
  | "clear"
  | "partly"
  | "cloud"
  | "fog"
  | "rain"
  | "snow"
  | "storm"
  | "unknown";

// ponytail: coarse wttr code buckets; extend map if a code renders wrong often.
const WEATHER_CODE_KIND: Record<number, WeatherConditionKind> = {
  113: "clear",
  116: "partly",
  119: "cloud",
  122: "cloud",
  143: "fog",
  176: "rain",
  179: "snow",
  182: "snow",
  185: "snow",
  200: "storm",
  227: "snow",
  230: "snow",
  248: "fog",
  260: "fog",
  263: "rain",
  266: "rain",
  281: "rain",
  284: "rain",
  293: "rain",
  296: "rain",
  299: "rain",
  302: "rain",
  305: "rain",
  308: "rain",
  311: "rain",
  314: "rain",
  317: "snow",
  320: "snow",
  323: "snow",
  326: "snow",
  329: "snow",
  332: "snow",
  335: "snow",
  338: "snow",
  350: "snow",
  353: "rain",
  356: "rain",
  359: "rain",
  362: "snow",
  365: "snow",
  368: "snow",
  371: "snow",
  374: "rain",
  377: "snow",
  386: "storm",
  389: "storm",
  392: "storm",
  395: "snow",
};

/** Condition kind for wttr.in weatherCode; falls back to description or unknown. */
export function weatherConditionKind(
  code: string | undefined,
  weatherDesc?: string,
): WeatherConditionKind {
  if (code) {
    const parsed = Number.parseInt(code, 10);
    if (Number.isFinite(parsed) && WEATHER_CODE_KIND[parsed]) {
      return WEATHER_CODE_KIND[parsed];
    }
  }
  const desc = weatherDesc?.toLowerCase() ?? "";
  if (desc.includes("sun") || desc.includes("clear")) return "clear";
  if (desc.includes("partly")) return "partly";
  if (desc.includes("cloud")) return "cloud";
  if (desc.includes("rain") || desc.includes("drizzle")) return "rain";
  if (desc.includes("snow")) return "snow";
  if (desc.includes("thunder") || desc.includes("storm")) return "storm";
  if (desc.includes("fog") || desc.includes("mist")) return "fog";
  return "unknown";
}
