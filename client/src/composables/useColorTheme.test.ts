import { afterEach, describe, expect, it, vi } from "vitest";

import {
  COLOR_THEME_STORAGE_KEY,
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

  it("resolveTheme maps system to OS preference", () => {
    vi.spyOn(window, "matchMedia").mockImplementation((query) => {
      return {
        matches: query.includes("dark"),
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        addListener: vi.fn(),
        removeListener: vi.fn(),
        dispatchEvent: vi.fn(),
        onchange: null,
      } as MediaQueryList;
    });
    expect(resolveTheme("system")).toBe("dark");
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
    expect(meta.getAttribute("content")).toBe("#f9f9fb");

    applyColorTheme("dark");
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
    expect(meta.getAttribute("content")).toBe("#111827");

    meta.remove();
  });

  it("storage key is stable for FOUC script parity", () => {
    expect(COLOR_THEME_STORAGE_KEY).toBe("glorng-color-theme");
  });
});
