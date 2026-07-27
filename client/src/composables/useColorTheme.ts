import { computed, onMounted, ref, type Ref } from "vue";

/** Persisted color theme (explicit light or dark only). */
export type ColorThemePreference = "light" | "dark";

/** Resolved theme applied to `html[data-theme]` — same as preference. */
export type ColorThemeResolved = ColorThemePreference;

export const COLOR_THEME_STORAGE_KEY = "glorng-color-theme";

/** Unset / invalid localStorage → dark (FOUC script must match). */
export const DEFAULT_COLOR_THEME_PREFERENCE: ColorThemePreference = "dark";

const THEME_COLOR_LIGHT = "#e5e7eb";
const THEME_COLOR_DARK = "#111827";

const preference: Ref<ColorThemePreference> = ref(readPreference());
/** Shared resolved theme — charts/composables can depend on this for reactivity. */
export const colorThemeResolved: Ref<ColorThemeResolved> = ref(preference.value);
const resolved = colorThemeResolved;

function systemPrefersDark(): boolean {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return true;
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

/** Map legacy `system` (or OS peek) to an explicit preference. */
function migrateLegacyPreference(raw: string | null | undefined): ColorThemePreference | null {
  if (raw === "light" || raw === "dark") return raw;
  if (raw === "system") {
    return systemPrefersDark() ? "dark" : "light";
  }
  return null;
}

function readPreference(): ColorThemePreference {
  if (typeof localStorage === "undefined") {
    return DEFAULT_COLOR_THEME_PREFERENCE;
  }
  try {
    const raw = localStorage.getItem(COLOR_THEME_STORAGE_KEY)?.trim();
    const migrated = migrateLegacyPreference(raw);
    if (migrated) {
      // ponytail: rewrite legacy `system` so toggle never resurfaces it
      if (raw === "system") {
        try {
          localStorage.setItem(COLOR_THEME_STORAGE_KEY, migrated);
        } catch {
          // ignore
        }
      }
      return migrated;
    }
  } catch {
    // ignore
  }
  return DEFAULT_COLOR_THEME_PREFERENCE;
}

export function resolveTheme(pref: ColorThemePreference): ColorThemeResolved {
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
    applyColorTheme(preference.value);
  });

  const isDark = computed(() => resolved.value === "dark");

  function setPreference(next: ColorThemePreference): void {
    preference.value = next;
    persistPreference(next);
    applyColorTheme(next);
  }

  /** Toggle dark ↔ light for a single chrome control. */
  function cyclePreference(): void {
    setPreference(preference.value === "dark" ? "light" : "dark");
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
  applyColorTheme(preference.value);
}
