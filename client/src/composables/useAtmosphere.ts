import { colorThemeResolved, syncThemeColorMeta } from "@/composables/useColorTheme";

/** Document attribute toggled by portfolio route meta. */
export const ATMOSPHERE_ATTR = "data-atmosphere";

export type AtmosphereKind = "space";

/**
 * Resolve route atmosphere from `meta.atmosphere`.
 * Unknown / missing values clear the attribute.
 */
export function resolveAtmosphere(meta: { atmosphere?: unknown }): AtmosphereKind | null {
  return meta.atmosphere === "space" ? "space" : null;
}

/** Whether the document currently has the space atmosphere. */
export function isSpaceAtmosphere(): boolean {
  if (typeof document === "undefined") {
    return false;
  }
  return document.documentElement.getAttribute(ATMOSPHERE_ATTR) === "space";
}

/**
 * Set or clear `html[data-atmosphere]` from the active route, then refresh
 * `theme-color` so the browser chrome matches space tokens while on `/`.
 */
export function applyRouteAtmosphere(to: { meta: { atmosphere?: unknown } }): void {
  if (typeof document === "undefined") {
    return;
  }
  const next = resolveAtmosphere(to.meta);
  if (next) {
    document.documentElement.setAttribute(ATMOSPHERE_ATTR, next);
  } else {
    document.documentElement.removeAttribute(ATMOSPHERE_ATTR);
  }
  syncThemeColorMeta(colorThemeResolved.value);
}
