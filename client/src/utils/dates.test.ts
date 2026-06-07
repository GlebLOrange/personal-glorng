import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  datetimeLocalValue,
  isValidDateRange,
  isValidDatetimeLocal,
  isValidIsoDate,
  isValidMonthValue,
  isoDateLocal,
  parseDatetimeLocalToIso,
} from "@/utils/dates";

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

describe("date validation helpers", () => {
  it("isValidIsoDate accepts valid dates and rejects invalid", () => {
    expect(isValidIsoDate("2025-06-07")).toBe(true);
    expect(isValidIsoDate("2025-02-30")).toBe(false);
    expect(isValidIsoDate("06-07-2025")).toBe(false);
  });

  it("isValidMonthValue accepts YYYY-MM months 01-12", () => {
    expect(isValidMonthValue("2025-06")).toBe(true);
    expect(isValidMonthValue("2025-13")).toBe(false);
    expect(isValidMonthValue("2025-00")).toBe(false);
  });

  it("isValidDatetimeLocal validates datetime-local shape", () => {
    expect(isValidDatetimeLocal("2025-06-07T23:30")).toBe(true);
    expect(isValidDatetimeLocal("2025-06-07")).toBe(false);
    expect(isValidDatetimeLocal("not-a-date")).toBe(false);
  });

  it("parseDatetimeLocalToIso returns ISO or null", () => {
    const iso = parseDatetimeLocalToIso("2025-06-07T12:00");
    expect(iso).not.toBeNull();
    expect(iso).toMatch(/2025-06-07T/);
    expect(parseDatetimeLocalToIso("bad")).toBeNull();
  });

  it("isValidDateRange enforces inclusive order", () => {
    expect(isValidDateRange("2025-06-01", "2025-06-30")).toBe(true);
    expect(isValidDateRange("2025-06-30", "2025-06-01")).toBe(false);
  });
});
