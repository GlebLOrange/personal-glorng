/**
 * @vitest-environment happy-dom
 */
import { describe, expect, it } from "vitest";

import {
  isExternalHref,
  isSafeNavigationUrl,
  safeNavigationHref,
  safeRouterPath,
} from "@/utils/safeUrl";

describe("safeNavigationHref", () => {
  it("allows same-origin relative paths", () => {
    expect(safeNavigationHref("/recipes")).toBe("/recipes");
    expect(safeNavigationHref("/tasks")).toBe("/tasks");
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

describe("safeRouterPath", () => {
  it("allows same-origin relative paths", () => {
    expect(safeRouterPath("/tasks")).toBe("/tasks");
    expect(safeRouterPath("/expenses?tab=insights")).toBe("/expenses?tab=insights");
  });

  it("rejects protocol-relative and dangerous schemes", () => {
    expect(safeRouterPath("//evil.example")).toBeNull();
    expect(safeRouterPath("javascript:alert(1)")).toBeNull();
  });

  it("allows same-origin absolute URLs as relative paths", () => {
    expect(safeRouterPath(`${window.location.origin}/tasks`)).toBe("/tasks");
  });

  it("rejects external https URLs", () => {
    expect(safeRouterPath("https://evil.example/doc")).toBeNull();
  });
});

describe("isExternalHref", () => {
  it("detects external https links", () => {
    expect(isExternalHref("https://example.com")).toBe(true);
    expect(isExternalHref("/recipes")).toBe(false);
  });
});
