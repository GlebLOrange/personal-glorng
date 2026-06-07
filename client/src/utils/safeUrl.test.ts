/**
 * @vitest-environment jsdom
 */
import { describe, expect, it } from "vitest";

import { isExternalHref, isSafeNavigationUrl, safeNavigationHref } from "@/utils/safeUrl";

describe("safeNavigationHref", () => {
  it("allows same-origin relative paths", () => {
    expect(safeNavigationHref("/recipes")).toBe("/recipes");
    expect(safeNavigationHref("/admin/tools/tasks")).toBe("/admin/tools/tasks");
  });

  it("rejects protocol-relative and dangerous schemes", () => {
    expect(safeNavigationHref("//evil.example")).toBeNull();
    expect(safeNavigationHref("javascript:alert(1)")).toBeNull();
    expect(safeNavigationHref("data:text/html,hi")).toBeNull();
  });

  it("allows same-origin absolute URLs as relative paths", () => {
    expect(safeNavigationHref(`${window.location.origin}/recipes`)).toBe("/recipes");
  });

  it("allows external https URLs", () => {
    expect(safeNavigationHref("https://example.com/doc")).toBe("https://example.com/doc");
  });

  it("rejects external http URLs", () => {
    expect(safeNavigationHref("http://example.com/doc")).toBeNull();
  });
});

describe("isSafeNavigationUrl", () => {
  it("mirrors safeNavigationHref nullability", () => {
    expect(isSafeNavigationUrl("/recipes")).toBe(true);
    expect(isSafeNavigationUrl("javascript:void(0)")).toBe(false);
  });
});

describe("isExternalHref", () => {
  it("detects external https links", () => {
    expect(isExternalHref("https://example.com")).toBe(true);
    expect(isExternalHref("/recipes")).toBe(false);
  });
});
