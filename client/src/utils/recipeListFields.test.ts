import { describe, expect, it } from "vitest";

import {
  filledListCount,
  insertBlankAfter,
  replaceWithPasteLines,
  splitPasteLines,
} from "@/utils/recipeListFields";

describe("recipeListFields", () => {
  it("counts filled trimmed lines", () => {
    expect(filledListCount(["a", "  ", "", "b"])).toBe(2);
  });

  it("splits paste lines and drops blanks", () => {
    expect(splitPasteLines("a\n\nb\r\nc  \n")).toEqual(["a", "b", "c"]);
  });

  it("inserts a blank row after an index", () => {
    expect(insertBlankAfter(["a", "b"], 0)).toEqual(["a", "", "b"]);
  });

  it("replaces a row with pasted lines", () => {
    expect(replaceWithPasteLines(["a", "b", "c"], 1, ["x", "y"])).toEqual([
      "a",
      "x",
      "y",
      "c",
    ]);
  });
});
