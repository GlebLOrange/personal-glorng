import { describe, expect, it } from "vitest";

import { safeRedirectPath } from "@/utils/safeUrl";

describe("safeRedirectPath", () => {
  it("allows relative in-app paths", () => {
    expect(safeRedirectPath("/expenses")).toBe("/expenses");
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

  it("rejects auth entry paths that would loop after login", () => {
    expect(safeRedirectPath("/login")).toBe("/admin");
    expect(safeRedirectPath("/login?redirect=/admin")).toBe("/admin");
    expect(safeRedirectPath("/register")).toBe("/admin");
    expect(safeRedirectPath("/forgot-password")).toBe("/admin");
    expect(safeRedirectPath("/reset-password")).toBe("/admin");
    expect(safeRedirectPath("/verify-email")).toBe("/admin");
    expect(safeRedirectPath("/callback")).toBe("/admin");
    expect(safeRedirectPath("/login/")).toBe("/admin");
  });
});
