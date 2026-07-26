/**
 * @vitest-environment happy-dom
 */
import { describe, expect, it } from "vitest";

import { safeImageSrc } from "@/utils/safeImageSrc";

describe("safeImageSrc", () => {
  it("returns null for empty input", () => {
    expect(safeImageSrc(null)).toBeNull();
    expect(safeImageSrc(undefined)).toBeNull();
    expect(safeImageSrc("   ")).toBeNull();
  });

  it("allows same-origin relative paths", () => {
    expect(safeImageSrc("/media/recipe.jpg")).toBe("/media/recipe.jpg");
  });

  it("rejects protocol-relative and dangerous schemes", () => {
    expect(safeImageSrc("//evil.example/img.png")).toBeNull();
    expect(safeImageSrc("javascript:alert(1)")).toBeNull();
    expect(safeImageSrc("data:image/png;base64,abc")).toBeNull();
    expect(safeImageSrc("blob:https://example.com/uuid")).toBeNull();
  });

  it("allows CSP-allowlisted https hosts", () => {
    expect(safeImageSrc("https://www.themealdb.com/images/media/meals/example.jpg")).toBe(
      "https://www.themealdb.com/images/media/meals/example.jpg",
    );
    expect(safeImageSrc("https://i.scdn.co/image/ab67616d0000b273")).toBe(
      "https://i.scdn.co/image/ab67616d0000b273",
    );
  });

  it("rejects https hosts outside the CSP allowlist", () => {
    expect(safeImageSrc("https://example.com/photo.jpg")).toBeNull();
  });

  it("rejects external http URLs", () => {
    expect(safeImageSrc("http://www.themealdb.com/photo.jpg")).toBeNull();
  });
});
