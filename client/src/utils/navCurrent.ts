/** Top-level main-nav sections that can receive aria-current="page". */
export type NavSection = "portfolio" | "news" | "tools" | "admin" | "settings" | "login";

/** Paths that belong under the Tools nav item (hub + tool pages). */
const TOOLS_NAV_PATHS = [
  "/tools",
  "/calculator",
  "/password-generator",
  "/qr-generator",
  "/recipes",
  "/shortener",
  "/weather",
  "/tasks",
  "/expenses",
  "/file-share",
  "/data-extract",
  "/vid-download",
  "/health-checker",
] as const;

function pathMatches(path: string, prefix: string): boolean {
  return path === prefix || path.startsWith(`${prefix}/`);
}

/** Which top-level nav item is current for this pathname. */
export function resolveNavSection(path: string): NavSection | null {
  const pathname = path.split("?")[0]?.split("#")[0] || "/";
  if (pathname === "/" || pathname === "") return "portfolio";
  if (pathMatches(pathname, "/news")) return "news";
  if (pathMatches(pathname, "/admin")) return "admin";
  if (pathMatches(pathname, "/settings")) return "settings";
  if (pathMatches(pathname, "/login")) return "login";
  if (TOOLS_NAV_PATHS.some((prefix) => pathMatches(pathname, prefix))) return "tools";
  return null;
}
