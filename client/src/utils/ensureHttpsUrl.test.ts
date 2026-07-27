import { describe, expect, it } from "vitest";

import { ensureHttpsUrl } from "@/utils/ensureHttpsUrl";

describe("ensureHttpsUrl", () => {
  it("leaves http(s) URLs unchanged aside from trim", () => {
    expect(ensureHttpsUrl("  https://example.com/path  ")).toBe("https://example.com/path");
    expect(ensureHttpsUrl("http://example.com")).toBe("http://example.com");
  });

  it("prepends https:// for scheme-less hosts", () => {
    expect(ensureHttpsUrl("example.com")).toBe("https://example.com");
    expect(ensureHttpsUrl("example.com/foo")).toBe("https://example.com/foo");
    expect(ensureHttpsUrl("www.example.com")).toBe("https://www.example.com");
  });

  it("normalizes protocol-relative URLs", () => {
    expect(ensureHttpsUrl("//cdn.example.com/a.js")).toBe("https://cdn.example.com/a.js");
  });

  it("leaves non-http schemes unchanged for the API to reject", () => {
    expect(ensureHttpsUrl("ftp://example.com")).toBe("ftp://example.com");
  });
});
