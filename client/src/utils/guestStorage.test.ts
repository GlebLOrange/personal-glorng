import { describe, expect, it } from "vitest";

import { nextNegativeId, trimField } from "@/utils/guestStorage";

describe("trimField", () => {
  it("trims and caps strings; rejects non-strings", () => {
    expect(trimField("  hello  ", 5)).toBe("hello");
    expect(trimField("abcdef", 3)).toBe("abc");
    expect(trimField(null, 10)).toBe("");
    expect(trimField(42, 10)).toBe("");
  });
});

describe("nextNegativeId", () => {
  it("returns -1 for empty lists and steps below the current min", () => {
    expect(nextNegativeId([])).toBe(-1);
    expect(nextNegativeId([{ id: 5 }, { id: 1 }])).toBe(-1);
    expect(nextNegativeId([{ id: -1 }, { id: -3 }])).toBe(-4);
  });
});
