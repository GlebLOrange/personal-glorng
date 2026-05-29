import { describe, expect, it } from "vitest";

import { sanitizeEmailHtml } from "@/utils/sanitizeEmailHtml";

describe("sanitizeEmailHtml", () => {
  it("keeps safe email markup", () => {
    const html = "<h1>Hi</h1><p>Hello <strong>world</strong></p>";
    expect(sanitizeEmailHtml(html)).toContain("<p>Hello");
    expect(sanitizeEmailHtml(html)).toContain("<strong>world</strong>");
  });

  it("strips script tags and event handlers", () => {
    const dirty = '<p onclick="alert(1)">x</p><script>alert(1)</script>';
    const clean = sanitizeEmailHtml(dirty);
    expect(clean).not.toContain("<script");
    expect(clean).not.toContain("onclick");
  });
});
