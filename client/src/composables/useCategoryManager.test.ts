import { describe, expect, it } from "vitest";

import {
  categoryNameExists,
  normalizeCategoryName,
  uniqueCategoryNames,
} from "@/composables/useCategoryManager";

describe("normalizeCategoryName", () => {
  it("trims and collapses whitespace", () => {
    expect(normalizeCategoryName("  Food   &  Drink ")).toBe("Food & Drink");
  });
});

describe("categoryNameExists", () => {
  const categories = [
    { id: 1, name: "Groceries" },
    { id: 2, name: "Home" },
  ];

  it("detects case-insensitive duplicates", () => {
    expect(categoryNameExists(categories, "groceries")).toBe(true);
    expect(categoryNameExists(categories, "  GROCERIES ")).toBe(true);
  });

  it("allows the same name when excluded by id", () => {
    expect(categoryNameExists(categories, "Groceries", 1)).toBe(false);
  });

  it("returns false for empty names", () => {
    expect(categoryNameExists(categories, "   ")).toBe(false);
  });
});

describe("uniqueCategoryNames", () => {
  it("keeps the first case-variant and drops later duplicates", () => {
    expect(
      uniqueCategoryNames([
        { name: "Groceries" },
        { name: "Home" },
        { name: "groceries" },
        { name: "Transport" },
      ]),
    ).toEqual(["Groceries", "Home", "Transport"]);
  });
});
