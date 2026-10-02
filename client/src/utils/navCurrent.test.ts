import { describe, expect, it } from "vitest";

import { resolveNavSection } from "@/utils/navCurrent";

describe("resolveNavSection", () => {
  it("marks portfolio on home", () => {
    expect(resolveNavSection("/")).toBe("portfolio");
  });

  it("marks news for list and article paths", () => {
    expect(resolveNavSection("/news")).toBe("news");
    expect(resolveNavSection("/news/some-slug")).toBe("news");
  });

  it("marks tools for the hub and public tool routes", () => {
    expect(resolveNavSection("/tools")).toBe("tools");
    expect(resolveNavSection("/weather")).toBe("tools");
    expect(resolveNavSection("/calculator")).toBe("tools");
    expect(resolveNavSection("/tasks")).toBe("tools");
  });

  it("marks admin for admin hub and nested admin routes", () => {
    expect(resolveNavSection("/admin")).toBe("admin");
    expect(resolveNavSection("/admin/users")).toBe("admin");
  });

  it("marks settings and login", () => {
    expect(resolveNavSection("/settings")).toBe("settings");
    expect(resolveNavSection("/login")).toBe("login");
  });

  it("returns null for unknown paths", () => {
    expect(resolveNavSection("/privacy")).toBeNull();
    expect(resolveNavSection("/register")).toBeNull();
  });
});
