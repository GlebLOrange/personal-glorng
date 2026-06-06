import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { datetimeLocalValue, isoDateLocal } from "@/utils/dates";

describe("dates", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2025-06-07T23:30:00+02:00"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("isoDateLocal uses local calendar date near midnight", () => {
    expect(isoDateLocal()).toBe("2025-06-07");
  });

  it("datetimeLocalValue uses local wall clock", () => {
    expect(datetimeLocalValue()).toBe("2025-06-07T23:30");
  });
});
