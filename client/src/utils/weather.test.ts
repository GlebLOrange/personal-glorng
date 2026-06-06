import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  formatLiveLocalDateTime,
  isoDateTimeFromOffset,
  localTimeFromOffset,
} from "@/utils/weather";

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
});
