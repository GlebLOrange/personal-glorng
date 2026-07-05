import { describe, expect, it } from "vitest";

import {
  computeIsScrollable,
  computeScrollProgress,
} from "@/composables/useScrollProgress";

describe("computeScrollProgress", () => {
  it("returns 0 at top and 1 at bottom", () => {
    expect(computeScrollProgress(0, 3000, 1000)).toBe(0);
    expect(computeScrollProgress(2000, 3000, 1000)).toBe(1);
  });

  it("returns ~0.32 below first third boundary", () => {
    expect(computeScrollProgress(640, 3000, 1000)).toBeCloseTo(0.32, 2);
  });

  it("returns ~0.33 at first third boundary", () => {
    expect(computeScrollProgress(660, 3000, 1000)).toBeCloseTo(0.33, 2);
  });

  it("returns ~0.99 near bottom", () => {
    expect(computeScrollProgress(1980, 3000, 1000)).toBeCloseTo(0.99, 2);
  });
});

describe("computeIsScrollable", () => {
  it("is false when content fits viewport", () => {
    expect(computeIsScrollable(1000, 1000)).toBe(false);
    expect(computeIsScrollable(1010, 1000)).toBe(false);
  });

  it("is true when content exceeds viewport threshold", () => {
    expect(computeIsScrollable(1020, 1000)).toBe(true);
  });
});
