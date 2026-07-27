import { describe, expect, it } from "vitest";

import { defaultToolsCategory, resolveToolsCategory } from "@/utils/toolsCategory";

describe("defaultToolsCategory", () => {
  it("prefers content when present", () => {
    expect(defaultToolsCategory(["productivity", "content", "utilities"])).toBe("content");
  });

  it("falls back to the first available category", () => {
    expect(defaultToolsCategory(["productivity", "utilities"])).toBe("productivity");
  });

  it("returns empty string when nothing is available", () => {
    expect(defaultToolsCategory([])).toBe("");
  });
});

describe("resolveToolsCategory", () => {
  const available = ["productivity", "content", "utilities"] as const;

  it("keeps a valid query category", () => {
    expect(resolveToolsCategory("utilities", available)).toBe("utilities");
  });

  it("defaults when query is missing", () => {
    expect(resolveToolsCategory(undefined, available)).toBe("content");
  });

  it("defaults when query is invalid", () => {
    expect(resolveToolsCategory("operations", available)).toBe("content");
  });

  it("ignores non-string query values", () => {
    expect(resolveToolsCategory(["content"], available)).toBe("content");
  });

  it("hides empty categories by only accepting available ids", () => {
    expect(resolveToolsCategory("productivity", ["content", "utilities"])).toBe("content");
  });
});
