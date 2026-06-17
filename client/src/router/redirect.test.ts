import { describe, expect, it } from "vitest";

import { safeRedirectPath } from "@/utils/safeUrl";

describe("safeRedirectPath", () => {
  it("allows relative in-app paths", () => {
    expect(safeRedirectPath("/admin/tools/expenses")).toBe("/admin/tools/expenses");
  });

  it("normalizes same-origin absolute URLs to paths", () => {
    expect(safeRedirectPath(`${window.location.origin}/admin?tab=tools#expenses`)).toBe(
      "/admin?tab=tools#expenses",
    );
  });

  it("rejects protocol-relative open redirects", () => {
    expect(safeRedirectPath("//evil.example")).toBe("/admin");
  });

  it("rejects absolute URLs", () => {
    expect(safeRedirectPath("https://evil.example")).toBe("/admin");
  });

  it("defaults when redirect is missing", () => {
    expect(safeRedirectPath(undefined)).toBe("/admin");
  });
});
