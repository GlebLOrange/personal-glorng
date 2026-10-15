import { describe, expect, it } from "vitest";

import { tileHintForSlug } from "@/constants/toolIntros";

describe("toolIntros", () => {
  it("returns tile hints only for ambiguous slugs", () => {
    expect(tileHintForSlug("health-checker")).toBe("Check uptime, latency, SSL, and DNS.");
    expect(tileHintForSlug("calculator")).toBeUndefined();
  });
});
