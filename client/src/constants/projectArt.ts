import type { ColorThemeResolved } from "@/composables/useColorTheme";

/** Locally served, text-free artwork for a project slug. */
export type ProjectArtPair = {
  light: string;
  dark: string;
};

const FALLBACK_ART: ProjectArtPair = {
  light: "/portfolio/fallback-light.svg",
  dark: "/portfolio/fallback-dark.svg",
};

/** Known resume project slugs → abstract systems art (decorative only). */
export const PROJECT_ART_BY_SLUG: Readonly<Record<string, ProjectArtPair>> = {
  "cookie-auth-csrf": {
    light: "/portfolio/cookie-auth-csrf-light.svg",
    dark: "/portfolio/cookie-auth-csrf-dark.svg",
  },
  "ssrf-safe-fetch": {
    light: "/portfolio/ssrf-safe-fetch-light.svg",
    dark: "/portfolio/ssrf-safe-fetch-dark.svg",
  },
};

/** Resolve light/dark artwork path for a project slug. */
export function projectArtForSlug(slug: string, theme: ColorThemeResolved): string {
  const pair = PROJECT_ART_BY_SLUG[slug] ?? FALLBACK_ART;
  return theme === "light" ? pair.light : pair.dark;
}
