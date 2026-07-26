const BLOCKED_PROTOCOLS = new Set(["javascript:", "data:", "vbscript:", "blob:"]);

/**
 * Hosts allowed by nginx img-src CSP (https only).
 * Keep in sync with nginx/security_headers.conf and security_headers.prod.conf.
 */
const CSP_IMG_HOSTS = new Set([
  "fastapi.tiangolo.com",
  "i.scdn.co",
  "www.paypal.com",
  "www.paypalobjects.com",
  "www.themealdb.com",
]);

/** Allow same-origin relative paths and CSP-allowlisted https hosts for img src. */
export function safeImageSrc(url: string | null | undefined): string | null {
  const trimmed = url?.trim();
  if (!trimmed) {
    return null;
  }

  if (trimmed.startsWith("/") && !trimmed.startsWith("//")) {
    return trimmed;
  }

  try {
    const parsed = new URL(trimmed);
    if (BLOCKED_PROTOCOLS.has(parsed.protocol)) {
      return null;
    }
    if (parsed.protocol === "https:" && CSP_IMG_HOSTS.has(parsed.hostname)) {
      return parsed.href;
    }
  } catch {
    return null;
  }

  return null;
}
