import { computed, onMounted, ref, type Ref } from "vue";

/** Persisted preference: explicit theme or follow OS. Default system when unset. */
export type ColorThemePreference = "light" | "dark" | "system";

/** Resolved theme applied to `html[data-theme]`. */
export type ColorThemeResolved = "light" | "dark";

export const COLOR_THEME_STORAGE_KEY = "glorng-color-theme";

/** Unset / invalid localStorage → follow OS (FOUC script must match). */
export const DEFAULT_COLOR_THEME_PREFERENCE: ColorThemePreference = "system";

const THEME_COLOR_LIGHT = "#f9f9fb";
const THEME_COLOR_DARK = "#111827";

let mediaQuery: MediaQueryList | null = null;
let mediaListener: ((event: MediaQueryListEvent) => void) | null = null;
const preference: Ref<ColorThemePreference> = ref(readPreference());
/** Shared resolved theme — charts/composables can depend on this for reactivity. */
export const colorThemeResolved: Ref<ColorThemeResolved> = ref(resolveTheme(preference.value));
const resolved = colorThemeResolved;

function readPreference(): ColorThemePreference {
  if (typeof localStorage === "undefined") {
    return DEFAULT_COLOR_THEME_PREFERENCE;
  }
  try {
    const raw = localStorage.getItem(COLOR_THEME_STORAGE_KEY)?.trim();
    if (raw === "light" || raw === "dark" || raw === "system") {
      return raw;
    }
  } catch {
    // ignore
  }
  return DEFAULT_COLOR_THEME_PREFERENCE;
}

function systemPrefersDark(): boolean {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return true;
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

export function resolveTheme(pref: ColorThemePreference): ColorThemeResolved {
  if (pref === "system") {
    return systemPrefersDark() ? "dark" : "light";
  }
  return pref;
}

function syncThemeColorMeta(theme: ColorThemeResolved): void {
  if (typeof document === "undefined") {
    return;
  }
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) {
    meta.setAttribute("content", theme === "light" ? THEME_COLOR_LIGHT : THEME_COLOR_DARK);
  }
}

/** Apply resolved theme to document (idempotent). */
export function applyColorTheme(theme: ColorThemeResolved): void {
  if (typeof document === "undefined") {
    return;
  }
  document.documentElement.setAttribute("data-theme", theme);
  syncThemeColorMeta(theme);
  colorThemeResolved.value = theme;
}

function persistPreference(pref: ColorThemePreference): void {
  if (typeof localStorage === "undefined") {
    return;
  }
  try {
    localStorage.setItem(COLOR_THEME_STORAGE_KEY, pref);
  } catch {
    // ignore
  }
}

function onSystemChange(): void {
  if (preference.value !== "system") {
    return;
  }
  applyColorTheme(resolveTheme("system"));
}

function ensureSystemListener(): void {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return;
  }
  if (mediaQuery && mediaListener) {
    return;
  }
  mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  mediaListener = (): void => {
    onSystemChange();
  };
  mediaQuery.addEventListener("change", mediaListener);
}

/**
 * Color theme preference + resolved `data-theme`.
 * Call `initColorTheme()` once at app boot (after FOUC script already painted).
 */
export function useColorTheme(): {
  preference: Ref<ColorThemePreference>;
  resolved: Ref<ColorThemeResolved>;
  isDark: Ref<boolean>;
  setPreference: (next: ColorThemePreference) => void;
  cyclePreference: () => void;
} {
  onMounted(() => {
    preference.value = readPreference();
    applyColorTheme(resolveTheme(preference.value));
    ensureSystemListener();
  });

  const isDark = computed(() => resolved.value === "dark");

  function setPreference(next: ColorThemePreference): void {
    preference.value = next;
    persistPreference(next);
    applyColorTheme(resolveTheme(next));
    if (next === "system") {
      ensureSystemListener();
    }
  }

  /** Cycle dark → light → system → dark for a single chrome control. */
  function cyclePreference(): void {
    const order: ColorThemePreference[] = ["dark", "light", "system"];
    const idx = order.indexOf(preference.value);
    const next = order[(idx + 1) % order.length] ?? "dark";
    setPreference(next);
  }

  return {
    preference,
    resolved,
    isDark,
    setPreference,
    cyclePreference,
  };
}

/** Sync Vue state after the FOUC inline script (call once from main.ts). */
export function initColorTheme(): void {
  preference.value = readPreference();
  applyColorTheme(resolveTheme(preference.value));
  ensureSystemListener();
}
