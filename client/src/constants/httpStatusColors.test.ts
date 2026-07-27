import { describe, expect, it } from "vitest";

import {
  actionFamilyClass,
  familyBadgeClass,
  httpStatusClass,
  httpStatusFamily,
  iconActionClass,
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
    expect(familyBadgeClass("1xx")).toContain("accent-blue");
  });

  it("uses /3 idle wash and selected/hover with border", () => {
    const idle = actionFamilyClass("2xx", false);
    expect(idle).toContain("font-medium");
    expect(idle).toContain("leading-none");
    expect(idle).toContain("border-transparent");
    expect(idle).toContain("bg-status-success/3");
    expect(idle).toContain("text-status-success");
    expect(idle).toContain("hover:enabled:bg-status-success/15");
    expect(idle).toContain("hover:enabled:border-status-success/40");

    const preview = actionFamilyClass("1xx", false);
    expect(preview).toContain("border-transparent");
    expect(preview).toContain("bg-accent-blue/3");
    expect(preview).toContain("text-accent-blue");
    expect(preview).toContain("hover:enabled:bg-accent-blue/15");
    expect(preview).toContain("hover:enabled:border-accent-blue/40");

    const selected = actionFamilyClass("2xx", true);
    expect(selected).toContain("font-medium");
    expect(selected).toContain("leading-none");
    expect(selected).toContain("bg-status-success/15");
    expect(selected).toContain("border-status-success/40");
  });

  it("builds h-10 icon action classes", () => {
    const icon = iconActionClass("3xx", false);
    expect(icon).toContain("h-10");
    expect(icon).toContain("box-border");
    expect(icon).toContain("bg-status-warning/3");
    expect(iconActionClass("1xx", false, { quiet: true })).toContain("text-surface-light/60");
    expect(iconActionClass("1xx", false, { danger: true })).toContain("bg-status-error/3");
    expect(iconActionClass("1xx", false, { anchor: true })).toContain("hover:bg-accent-blue/15");
    expect(iconActionClass("1xx", false, { anchor: true })).not.toContain("hover:enabled:");
  });

  it("builds field-size icon action classes matching chrome", () => {
    const field = iconActionClass("4xx", false, { size: "field", danger: true });
    expect(field).toContain("!h-full");
    expect(field).toContain("!w-10");
    expect(field).toContain("bg-status-error/3");
  });
});
