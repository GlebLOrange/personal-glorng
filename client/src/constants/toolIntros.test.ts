import { describe, expect, it } from "vitest";

import { publicTileBlurbForSlug, tileHintForSlug } from "@/constants/toolIntros";

describe("toolIntros", () => {
  it("returns tile hints only for ambiguous slugs", () => {
    expect(tileHintForSlug("health-checker")).toBe("Check uptime, latency, SSL, and DNS.");
    expect(tileHintForSlug("calculator")).toBeUndefined();
  });

  it("returns a one-line blurb for every public tool slug", () => {
    expect(publicTileBlurbForSlug("weather")).toBe("Check the weather and local time.");
    expect(publicTileBlurbForSlug("url-shortener")).toBe("Shorten a long link.");
    expect(publicTileBlurbForSlug("recipes")).toBe("Open a recipe book and food notes.");
    expect(publicTileBlurbForSlug("calculator")).toBe("Do a quick calculation.");
    expect(publicTileBlurbForSlug("password-generator")).toBe("Create a strong password.");
    expect(publicTileBlurbForSlug("qr-generator")).toBe("Make a QR code from text or a link.");
  });
});
