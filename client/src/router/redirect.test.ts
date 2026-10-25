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
    expect(safeRedirectPath("//evil.example")).toBe("/tools");
  });

  it("rejects absolute URLs", () => {
    expect(safeRedirectPath("https://evil.example")).toBe("/tools");
  });

  it("defaults when redirect is missing", () => {
    expect(safeRedirectPath(undefined)).toBe("/tools");
  });

  it("rejects auth entry paths that would loop after login", () => {
    expect(safeRedirectPath("/login")).toBe("/tools");
    expect(safeRedirectPath("/login?redirect=/admin")).toBe("/tools");
    expect(safeRedirectPath("/register")).toBe("/tools");
    expect(safeRedirectPath("/forgot-password")).toBe("/tools");
    expect(safeRedirectPath("/reset-password")).toBe("/tools");
    expect(safeRedirectPath("/verify-email")).toBe("/tools");
    expect(safeRedirectPath("/callback")).toBe("/tools");
    expect(safeRedirectPath("/login/")).toBe("/tools");
  });
});
