import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { WeatherData } from "@/types";

import {
  formatLiveLocalDate,
  formatLiveLocalDateFromUnix,
  formatLiveLocalDateTime,
  formatLiveLocalTimeFromIana,
  formatLiveLocalTimeWithSecondsFromUnix,
  isoDateTimeFromOffset,
  isValidWeatherLocationQuery,
  localTimeFromOffset,
  weatherAnchorUnixtime,
  weatherConditionEmoji,
  weatherIanaTimezone,
  weatherUtcOffsetHours,
} from "@/utils/weather";
import { sanitizeGuestWeatherLocations } from "@/utils/guestWeatherLocations";

describe("weather time formatting", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2025-06-07T12:00:00Z"));
    vi.spyOn(Date.prototype, "getTimezoneOffset").mockReturnValue(0);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("localTimeFromOffset uses UTC fields for target offset", () => {
    const parts = localTimeFromOffset(3);
    expect(parts.hours24).toBe(15);
    expect(parts.minutes).toBe(0);
  });

  it("formatLiveLocalDateTime matches offset wall clock", () => {
    expect(formatLiveLocalDateTime(3)).toBe("Sat Jun 7 3:00 pm");
  });

  it("isoDateTimeFromOffset returns ISO-like datetime", () => {
    expect(isoDateTimeFromOffset(3)).toBe("2025-06-07T15:00:00");
  });

  it("formatLiveLocalTimeWithSecondsFromUnix formats anchored wall clock", () => {
    expect(formatLiveLocalTimeWithSecondsFromUnix(1_780_833_600, 2)).toBe("14:00:00");
  });

  it("formatLiveLocalDate matches offset wall clock", () => {
    expect(formatLiveLocalDate(3)).toBe("Sat, Jun 7");
  });

  it("formatLiveLocalDateFromUnix formats anchored wall date", () => {
    expect(formatLiveLocalDateFromUnix(1_780_833_600, 2)).toBe("Sun, Jun 7");
  });
});

describe("weatherConditionEmoji", () => {
  it("maps known wttr codes", () => {
    expect(weatherConditionEmoji("113")).toBe("☀️");
    expect(weatherConditionEmoji("296")).toBe("🌧️");
  });

  it("falls back to description or generic icon", () => {
    expect(weatherConditionEmoji(undefined, "Partly cloudy")).toBe("☁️");
    expect(weatherConditionEmoji("99999")).toBe("🌡️");
  });
});

describe("weather time_zone helpers", () => {
  const weatherWithAnchor: WeatherData = {
    current_condition: [{ temp_C: "20" }],
    time_zone: [
      {
        utcOffset: "+02:00",
        timezone: "Europe/Warsaw",
        unixtime: 1_780_833_600,
      },
    ],
  };

  it("weatherAnchorUnixtime returns unixtime when present", () => {
    expect(weatherAnchorUnixtime(weatherWithAnchor)).toBe(1_780_833_600);
  });

  it("weatherAnchorUnixtime returns null when missing", () => {
    expect(weatherAnchorUnixtime({ current_condition: [] })).toBeNull();
  });

  it("weatherUtcOffsetHours parses colon offsets", () => {
    expect(weatherUtcOffsetHours(weatherWithAnchor)).toBe(2);
  });

  it("weatherIanaTimezone extracts IANA id", () => {
    expect(weatherIanaTimezone(weatherWithAnchor)).toBe("Europe/Warsaw");
    expect(weatherIanaTimezone({ current_condition: [] })).toBeNull();
  });
});

describe("IANA timezone formatting", () => {
  it("formatLiveLocalTimeFromIana shows CEST wall clock for Warsaw", () => {
    const at = new Date("2026-07-14T01:35:00Z");
    expect(formatLiveLocalTimeFromIana("Europe/Warsaw", at)).toBe("03:35");
  });
});

describe("isValidWeatherLocationQuery", () => {
  it("accepts city names and coordinates", () => {
    expect(isValidWeatherLocationQuery("Wroclaw")).toBe(true);
    expect(isValidWeatherLocationQuery("51.1,17.0")).toBe(true);
  });

  it("rejects invalid queries", () => {
    expect(isValidWeatherLocationQuery("Paris123")).toBe(false);
    expect(isValidWeatherLocationQuery("<script>")).toBe(false);
  });
});

describe("sanitizeGuestWeatherLocations", () => {
  it("caps entries and drops invalid records", () => {
    const raw = [
      { id: "1", label: "A", query: "London", sort_order: 0 },
      { id: "2", label: "Bad", query: "Paris123", sort_order: 1 },
      { id: "3", label: "B", query: "London", sort_order: 2 },
      { id: "4", label: "C", query: "Paris", sort_order: 3 },
    ];
    const sanitized = sanitizeGuestWeatherLocations(raw);
    expect(sanitized).toHaveLength(2);
    expect(sanitized.map((loc) => loc.query)).toEqual(["London", "Paris"]);
  });
});
