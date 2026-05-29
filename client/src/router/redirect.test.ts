import { describe, expect, it } from "vitest";

/** Mirror login redirect guard in router/index.ts */
function loginRedirectTarget(redirect: unknown): string {
  return typeof redirect === "string" &&
    redirect.startsWith("/") &&
    !redirect.startsWith("//")
    ? redirect
    : "/admin";
}

describe("loginRedirectTarget", () => {
  it("allows relative in-app paths", () => {
    expect(loginRedirectTarget("/admin/tools/expenses")).toBe(
      "/admin/tools/expenses",
    );
  });

  it("rejects protocol-relative open redirects", () => {
    expect(loginRedirectTarget("//evil.example")).toBe("/admin");
  });

  it("rejects absolute URLs", () => {
    expect(loginRedirectTarget("https://evil.example")).toBe("/admin");
  });

  it("defaults when redirect is missing", () => {
    expect(loginRedirectTarget(undefined)).toBe("/admin");
  });
});
