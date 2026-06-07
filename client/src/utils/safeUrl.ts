const BLOCKED_PROTOCOLS = new Set(["javascript:", "data:", "vbscript:"]);

/** Whether a URL is safe to use as a navigation href in chat source links. */
export function isSafeNavigationUrl(url: string): boolean {
  return safeNavigationHref(url) !== null;
}

/**
 * Return a safe href for in-app navigation, or null when the URL must not be linked.
 * Allows same-origin relative paths and same-origin or https absolute URLs.
 */
export function safeNavigationHref(url: string): string | null {
  const trimmed = url.trim();
  if (!trimmed) {
    return null;
  }

  if (trimmed.startsWith("/") && !trimmed.startsWith("//")) {
    return trimmed;
  }

  try {
    const parsed = new URL(trimmed, window.location.origin);
    if (BLOCKED_PROTOCOLS.has(parsed.protocol)) {
      return null;
    }
    if (parsed.origin === window.location.origin) {
      return `${parsed.pathname}${parsed.search}${parsed.hash}`;
    }
    if (parsed.protocol === "https:") {
      return parsed.href;
    }
  } catch {
    return null;
  }

  return null;
}

/** True when the href points off-site (external https link). */
export function isExternalHref(href: string): boolean {
  if (href.startsWith("/")) {
    return false;
  }
  try {
    return new URL(href).origin !== window.location.origin;
  } catch {
    return false;
  }
}
