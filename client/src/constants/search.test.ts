import { describe, expect, it } from "vitest";

import { SEARCH_MIN_QUERY_LENGTH, effectiveSearchQuery } from "@/constants/search";

describe("effectiveSearchQuery", () => {
  it("returns undefined for empty and short queries", () => {
    expect(effectiveSearchQuery("")).toBeUndefined();
    expect(effectiveSearchQuery("  ")).toBeUndefined();
    expect(effectiveSearchQuery("ab")).toBeUndefined();
    expect(effectiveSearchQuery(" a ")).toBeUndefined();
  });

  it("returns the trimmed query at the minimum length", () => {
    expect(SEARCH_MIN_QUERY_LENGTH).toBe(3);
    expect(effectiveSearchQuery("abc")).toBe("abc");
    expect(effectiveSearchQuery("  pasta  ")).toBe("pasta");
  });
});
