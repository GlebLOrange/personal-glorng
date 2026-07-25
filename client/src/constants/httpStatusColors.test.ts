import { describe, expect, it } from "vitest";

import {
  actionFamilyClass,
  httpStatusClass,
  httpStatusFamily,
} from "@/constants/httpStatusColors";

describe("httpStatusColors", () => {
  it("maps codes to families", () => {
    expect(httpStatusFamily(101)).toBe("1xx");
    expect(httpStatusFamily(200)).toBe("2xx");
    expect(httpStatusFamily(301)).toBe("3xx");
    expect(httpStatusFamily(404)).toBe("4xx");
    expect(httpStatusFamily(503)).toBe("5xx");
  });

  it("returns pale badge classes per family", () => {
    expect(httpStatusClass(200)).toContain("status-success");
    expect(httpStatusClass(404)).toContain("status-error");
    expect(httpStatusClass(503)).toContain("status-critical");
  });

  it("keeps idle action pills text-only and selected with bg+border", () => {
    const idle = actionFamilyClass("2xx", false);
    expect(idle).toContain("border-transparent");
    expect(idle).toContain("hover:enabled:bg-status-success/15");
    expect(idle).toContain("hover:enabled:border-status-success/40");

    const preview = actionFamilyClass("1xx", false);
    expect(preview).toContain("border-transparent");
    expect(preview).toContain("hover:enabled:bg-accent-blue/15");
    expect(preview).toContain("hover:enabled:border-accent-blue/40");

    const selected = actionFamilyClass("2xx", true);
    expect(selected).toContain("bg-status-success/15");
    expect(selected).toContain("border-status-success/40");
  });
});
