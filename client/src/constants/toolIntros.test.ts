import { describe, expect, it } from "vitest";

import { publicTileBlurbForSlug, tileHintForSlug } from "@/constants/toolIntros";

describe("toolIntros", () => {
  it("returns tile hints only for ambiguous slugs", () => {
    expect(tileHintForSlug("health-checker")).toBe("uptime and dns");
    expect(tileHintForSlug("calculator")).toBeUndefined();
  });

  it("returns a few lowercase words for every tools-page slug", () => {
    const lines: Record<string, string> = {
      weather: "local weather and time",
      "url-shortener": "short links",
      recipes: "recipes and notes",
      calculator: "quick math",
      "password-generator": "strong passwords",
      "qr-generator": "qr from a link",
      tasks: "tasks and reminders",
      expenses: "track spending",
      "file-share": "share files",
      "vid-download": "save videos",
      "data-extract": "rows from files",
      news: "news digest",
      email: "send email",
    };
    for (const [slug, line] of Object.entries(lines)) {
      expect(publicTileBlurbForSlug(slug)).toBe(line);
      expect(line).toBe(line.toLowerCase());
      expect(line.split(/\s+/).length).toBeLessThanOrEqual(4);
    }
  });
});
