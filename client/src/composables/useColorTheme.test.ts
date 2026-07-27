import { afterEach, describe, expect, it, vi } from "vitest";

import {
  COLOR_THEME_STORAGE_KEY,
  DEFAULT_COLOR_THEME_PREFERENCE,
  applyColorTheme,
  resolveTheme,
} from "@/composables/useColorTheme";

describe("useColorTheme", () => {
  afterEach(() => {
    try {
      localStorage?.clear();
    } catch {
      // jsdom / node may omit localStorage
    }
    document.documentElement.removeAttribute("data-theme");
    vi.restoreAllMocks();
  });

  it("resolveTheme is identity for light/dark", () => {
    expect(resolveTheme("light")).toBe("light");
    expect(resolveTheme("dark")).toBe("dark");
  });

  it("applyColorTheme sets data-theme and theme-color meta", () => {
    const meta = document.createElement("meta");
    meta.setAttribute("name", "theme-color");
    meta.setAttribute("content", "#111827");
    document.head.appendChild(meta);

    applyColorTheme("light");
    expect(document.documentElement.getAttribute("data-theme")).toBe("light");
    expect(meta.getAttribute("content")).toBe("#e5e7eb");

    applyColorTheme("dark");
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
    expect(meta.getAttribute("content")).toBe("#111827");

    meta.remove();
  });

  it("storage key is stable for FOUC script parity", () => {
    expect(COLOR_THEME_STORAGE_KEY).toBe("glorng-color-theme");
  });

  it("unset preference defaults to dark (FOUC parity)", () => {
    expect(DEFAULT_COLOR_THEME_PREFERENCE).toBe("dark");
  });
});
