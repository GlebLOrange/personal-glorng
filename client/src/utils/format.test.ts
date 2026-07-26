import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  displayBreadcrumbLabel,
  formatBreadcrumbLabel,
  formatRelativeTime,
  formatScheduleDate,
  truncateBreadcrumbSlug,
  truncateBreadcrumbTitle,
} from "@/utils/format";

describe("formatBreadcrumbLabel", () => {
  it("keeps multi-word titles as a lowercase phrase", () => {
    expect(formatBreadcrumbLabel("app logs")).toBe("app logs");
    expect(formatBreadcrumbLabel("news sources")).toBe("news sources");
    expect(formatBreadcrumbLabel("edit news article")).toBe("edit news article");
    expect(formatBreadcrumbLabel("password generator")).toBe("password generator");
  });

  it("keeps kebab-case labels intact for article slugs", () => {
    expect(formatBreadcrumbLabel("url-shortener")).toBe("url-shortener");
    expect(formatBreadcrumbLabel("my-news-article")).toBe("my-news-article");
  });

  it("strips an existing section mark before normalizing", () => {
    expect(formatBreadcrumbLabel("§ tools")).toBe("tools");
    expect(formatBreadcrumbLabel("§expenses")).toBe("expenses");
  });

  it("preserves path-shaped labels for news edit crumbs", () => {
    expect(formatBreadcrumbLabel("news/my-slug")).toBe("news/my-slug");
    expect(displayBreadcrumbLabel("news/my-slug")).toBe("news/my-slug");
  });
});

describe("truncateBreadcrumbSlug", () => {
  it("returns short slugs unchanged", () => {
    expect(truncateBreadcrumbSlug("hello-world")).toBe("hello-world");
  });

  it("truncates long slugs to 14 characters with an ellipsis", () => {
    expect(truncateBreadcrumbSlug("this-is-a-very-long-news-slug")).toBe("this-is-a-very…");
    expect(truncateBreadcrumbSlug("this-is-a-very-long-news-slug").length).toBe(15);
  });
});

describe("displayBreadcrumbLabel", () => {
  it("aliases formatBreadcrumbLabel without a § prefix", () => {
    expect(displayBreadcrumbLabel("calculator")).toBe("calculator");
    expect(displayBreadcrumbLabel("app logs")).toBe("app logs");
    expect(displayBreadcrumbLabel("§ tools")).toBe("tools");
  });
});

describe("truncateBreadcrumbTitle", () => {
  it("returns the only word unchanged", () => {
    expect(truncateBreadcrumbTitle("Breaking")).toBe("Breaking");
  });

  it("keeps the first word and appends ellipsis", () => {
    expect(truncateBreadcrumbTitle("Breaking news about space")).toBe("Breaking...");
  });

  it("trims surrounding whitespace", () => {
    expect(truncateBreadcrumbTitle("  Hello world  ")).toBe("Hello...");
  });
});

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

  it("returns Today at time for near future same day", () => {
    const result = formatScheduleDate("2025-06-07T13:00:00");
    expect(result.headline).toBe("Today at 1:00 pm");
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
