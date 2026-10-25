import { describe, expect, it } from "vitest";

import { projectArtForSlug } from "@/constants/projectArt";

describe("projectArtForSlug", () => {
  it("maps known slugs to light and dark artwork", () => {
    expect(projectArtForSlug("cookie-auth-csrf", "dark")).toBe(
      "/portfolio/cookie-auth-csrf-dark.svg",
    );
    expect(projectArtForSlug("ssrf-safe-fetch", "light")).toBe(
      "/portfolio/ssrf-safe-fetch-light.svg",
    );
  });

  it("falls back for unknown slugs", () => {
    expect(projectArtForSlug("missing", "dark")).toBe("/portfolio/fallback-dark.svg");
    expect(projectArtForSlug("missing", "light")).toBe("/portfolio/fallback-light.svg");
  });
});
