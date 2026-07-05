import type { Router, RouteLocationNormalized, ScrollPosition } from "vue-router";

const STORAGE_PREFIX = "glorng:scroll:";

const fingerprints = new Map<string, string>();

export type ScrollRestoreMode = "stable" | "live" | "volatile";

interface ScrollSnapshot {
  y: number;
  fingerprint: string;
}

declare module "vue-router" {
  interface RouteMeta {
    scrollRestore?: ScrollRestoreMode;
  }
}

/** Register list-state fingerprint for volatile scroll restore on a route path. */
export function setScrollFingerprint(path: string, fingerprint: string): void {
  if (!path) return;
  fingerprints.set(path, fingerprint);
}

/** Read the current fingerprint for a route path. */
export function getScrollFingerprint(path: string): string {
  return fingerprints.get(path) ?? "";
}

/** Drop fingerprint when a volatile page unmounts. */
export function clearScrollFingerprint(path: string): void {
  if (!path) return;
  fingerprints.delete(path);
}

function storageKey(path: string): string {
  return `${STORAGE_PREFIX}${path}`;
}

/** Persist scroll Y and fingerprint when leaving a route. */
export function saveScrollSnapshot(path: string, y: number, fingerprint: string): void {
  if (!path) return;
  const snapshot: ScrollSnapshot = { y, fingerprint };
  sessionStorage.setItem(storageKey(path), JSON.stringify(snapshot));
}

/** Read a stored scroll snapshot for a route path. */
export function readScrollSnapshot(path: string): ScrollSnapshot | null {
  const raw = sessionStorage.getItem(storageKey(path));
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as ScrollSnapshot;
    if (typeof parsed.y === "number" && typeof parsed.fingerprint === "string") {
      return parsed;
    }
  } catch {
    // ponytail: corrupt snapshot → treat as missing
  }
  return null;
}

function getScrollRestoreMode(to: RouteLocationNormalized): ScrollRestoreMode {
  const mode = to.meta.scrollRestore;
  if (mode === "live" || mode === "volatile") return mode;
  return "stable";
}

/** Resolve scroll position for router scrollBehavior (back navigation only). */
export function resolveScrollBehavior(
  to: RouteLocationNormalized,
  savedPosition: ScrollPosition | null,
): ScrollPosition {
  if (savedPosition === null) {
    return { top: 0 };
  }

  const mode = getScrollRestoreMode(to);
  if (mode === "live") {
    return { top: 0 };
  }

  const snapshot = readScrollSnapshot(to.fullPath);
  if (!snapshot) {
    return savedPosition;
  }

  if (mode === "volatile") {
    const current = getScrollFingerprint(to.fullPath);
    if (current !== snapshot.fingerprint) {
      return { top: 0 };
    }
  }

  return { top: snapshot.y };
}

/** Save scroll snapshots on route leave. */
export function installScrollRestore(router: Router): void {
  router.beforeEach((to, from) => {
    if (!from.fullPath || from.fullPath === to.fullPath) return;
    saveScrollSnapshot(from.fullPath, window.scrollY, getScrollFingerprint(from.fullPath));
  });
}
