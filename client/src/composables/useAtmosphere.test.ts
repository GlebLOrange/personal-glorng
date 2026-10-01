import { afterEach, describe, expect, it } from "vitest";

import {
  applyRouteAtmosphere,
  ATMOSPHERE_ATTR,
  isSpaceAtmosphere,
  resolveAtmosphere,
} from "@/composables/useAtmosphere";
import {
  applyColorTheme,
  THEME_COLOR_SPACE_DARK,
  THEME_COLOR_SPACE_LIGHT,
} from "@/composables/useColorTheme";

describe("useAtmosphere", () => {
  afterEach(() => {
    document.documentElement.removeAttribute(ATMOSPHERE_ATTR);
    document.documentElement.removeAttribute("data-theme");
    document.querySelector('meta[name="theme-color"]')?.remove();
  });

  it("resolveAtmosphere maps space meta only", () => {
    expect(resolveAtmosphere({ atmosphere: "space" })).toBe("space");
    expect(resolveAtmosphere({})).toBeNull();
    expect(resolveAtmosphere({ atmosphere: "nebula" })).toBeNull();
  });

  it("applyRouteAtmosphere sets attribute on portfolio meta and clears on tools", () => {
    const meta = document.createElement("meta");
    meta.setAttribute("name", "theme-color");
    meta.setAttribute("content", "#0d1117");
    document.head.appendChild(meta);
    applyColorTheme("dark");

    applyRouteAtmosphere({ meta: { atmosphere: "space" } });
    expect(document.documentElement.getAttribute(ATMOSPHERE_ATTR)).toBe("space");
    expect(isSpaceAtmosphere()).toBe(true);
    expect(meta.getAttribute("content")).toBe(THEME_COLOR_SPACE_DARK);

    applyRouteAtmosphere({ meta: {} });
    expect(document.documentElement.getAttribute(ATMOSPHERE_ATTR)).toBeNull();
    expect(isSpaceAtmosphere()).toBe(false);
    expect(meta.getAttribute("content")).toBe("#0d1117");
  });

  it("theme toggle keeps space theme-color while atmosphere is active", () => {
    const meta = document.createElement("meta");
    meta.setAttribute("name", "theme-color");
    document.head.appendChild(meta);

    applyRouteAtmosphere({ meta: { atmosphere: "space" } });
    applyColorTheme("light");
    expect(meta.getAttribute("content")).toBe(THEME_COLOR_SPACE_LIGHT);

    applyColorTheme("dark");
    expect(meta.getAttribute("content")).toBe(THEME_COLOR_SPACE_DARK);
  });
});
