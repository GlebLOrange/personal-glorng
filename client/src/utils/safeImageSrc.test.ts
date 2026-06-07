/**
 * @vitest-environment jsdom
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

  it("allows external https URLs", () => {
    expect(safeImageSrc("https://example.com/photo.jpg")).toBe(
      "https://example.com/photo.jpg",
    );
  });

  it("rejects external http URLs", () => {
    expect(safeImageSrc("http://example.com/photo.jpg")).toBeNull();
  });
});
