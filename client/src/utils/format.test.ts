import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { formatRelativeTime, formatScheduleDate } from "@/utils/format";

describe("formatScheduleDate", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2025-06-07T12:00:00"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("returns Today for same calendar day", () => {
    const result = formatScheduleDate("2025-06-07T15:30:00");
    expect(result.headline).toMatch(/^Today at /);
    expect(result.detail).toContain("7 Jun 2025");
  });

  it("returns Tomorrow for next calendar day", () => {
    const result = formatScheduleDate("2025-06-08T09:00:00");
    expect(result.headline).toMatch(/^Tomorrow at /);
    expect(result.detail).toContain("8 Jun 2025");
  });

  it("returns Yesterday for previous calendar day", () => {
    const result = formatScheduleDate("2025-06-06T18:00:00");
    expect(result.headline).toMatch(/^Yesterday at /);
    expect(result.detail).toContain("6 Jun 2025");
  });

  it("returns In N hours for near future same day", () => {
    const result = formatScheduleDate("2025-06-07T13:00:00");
    expect(result.headline).toBe("In 1 hour");
  });

  it("returns N days ago for recent past", () => {
    const result = formatScheduleDate("2025-06-05T12:00:00");
    expect(result.headline).toBe("2 days ago");
  });
});

describe("formatRelativeTime", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2025-06-07T12:00:00"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("returns just now for recent timestamps", () => {
    expect(formatRelativeTime("2025-06-07T11:59:30")).toBe("just now");
  });

  it("returns minutes ago", () => {
    expect(formatRelativeTime("2025-06-07T11:45:00")).toBe("15 minutes ago");
  });

  it("returns hours ago", () => {
    expect(formatRelativeTime("2025-06-07T09:00:00")).toBe("3 hours ago");
  });

  it("returns days ago", () => {
    expect(formatRelativeTime("2025-06-05T12:00:00")).toBe("2 days ago");
  });
});
