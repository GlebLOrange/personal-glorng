import { describe, expect, it } from "vitest";

import { publicUrl } from "@/utils/publicLinks";

describe("publicUrl", () => {
  it("encodes code path segments", () => {
    expect(publicUrl("s", "abc")).toBe(`${window.location.origin}/s/abc`);
    expect(publicUrl("s", "a/b")).toBe(`${window.location.origin}/s/a%2Fb`);
    expect(publicUrl("/f", "x?y")).toBe(`${window.location.origin}/f/x%3Fy`);
  });
});
