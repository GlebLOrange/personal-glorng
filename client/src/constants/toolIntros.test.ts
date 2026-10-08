import { describe, expect, it } from "vitest";

import { introForRoute, tileHintForSlug } from "@/constants/toolIntros";

describe("toolIntros", () => {
  it("returns a page intro for a known route name", () => {
    expect(introForRoute("calculator")).toBe(
      "Add, subtract, multiply, and divide. The result is computed on the server.",
    );
  });

  it("returns nothing for an unknown route name", () => {
    expect(introForRoute("tools")).toBeUndefined();
    expect(introForRoute(undefined)).toBeUndefined();
  });

  it("returns tile hints only for ambiguous slugs", () => {
    expect(tileHintForSlug("health-checker")).toBe("Check uptime, latency, SSL, and DNS.");
    expect(tileHintForSlug("calculator")).toBeUndefined();
  });
});
