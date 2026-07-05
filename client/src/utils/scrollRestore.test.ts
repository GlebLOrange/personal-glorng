import { beforeEach, describe, expect, it, vi } from "vitest";
import type { RouteLocationNormalized } from "vue-router";

import {
  clearScrollFingerprint,
  readScrollSnapshot,
  resolveScrollBehavior,
  saveScrollSnapshot,
  setScrollFingerprint,
} from "@/utils/scrollRestore";

function route(
  fullPath: string,
  scrollRestore?: "stable" | "live" | "volatile",
): RouteLocationNormalized {
  return {
    fullPath,
    meta: scrollRestore ? { scrollRestore } : {},
  } as RouteLocationNormalized;
}

describe("scrollRestore", () => {
  beforeEach(() => {
    sessionStorage.clear();
    clearScrollFingerprint("/news");
    clearScrollFingerprint("/");
    vi.restoreAllMocks();
  });

  it("saves and reads scroll snapshots", () => {
    saveScrollSnapshot("/news", 420, "1:10:abc");
    expect(readScrollSnapshot("/news")).toEqual({ y: 420, fingerprint: "1:10:abc" });
    expect(readScrollSnapshot("/missing")).toBeNull();
  });

  it("returns top on forward navigation", () => {
    expect(resolveScrollBehavior(route("/"), null)).toEqual({ top: 0 });
  });

  it("restores stable route Y on back navigation", () => {
    saveScrollSnapshot("/", 800, "");
    expect(resolveScrollBehavior(route("/"), { left: 0, top: 0 })).toEqual({ top: 800 });
  });

  it("returns top on back to live routes", () => {
    saveScrollSnapshot("/weather", 500, "");
    expect(
      resolveScrollBehavior(route("/weather", "live"), { left: 0, top: 0 }),
    ).toEqual({ top: 0 });
  });

  it("restores volatile route Y when fingerprint matches", () => {
    saveScrollSnapshot("/news", 300, "2:40:item-1");
    setScrollFingerprint("/news", "2:40:item-1");
    expect(
      resolveScrollBehavior(route("/news", "volatile"), { left: 0, top: 0 }),
    ).toEqual({ top: 300 });
  });

  it("returns top on volatile back when fingerprint mismatches", () => {
    saveScrollSnapshot("/news", 300, "2:40:item-1");
    setScrollFingerprint("/news", "3:40:item-9");
    expect(
      resolveScrollBehavior(route("/news", "volatile"), { left: 0, top: 0 }),
    ).toEqual({ top: 0 });
  });

  it("falls back to browser savedPosition when no snapshot exists", () => {
    const saved = { left: 0, top: 150 };
    expect(resolveScrollBehavior(route("/"), saved)).toEqual(saved);
  });
});
