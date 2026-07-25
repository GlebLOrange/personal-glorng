/** Query keys that must not appear in history, analytics, SEO, or telemetry. */
const SENSITIVE_QUERY_KEYS = new Set(["token", "code", "state"]);

function scrubSearchParams(params: URLSearchParams): void {
  for (const key of [...params.keys()]) {
    if (SENSITIVE_QUERY_KEYS.has(key.toLowerCase())) {
      params.delete(key);
    }
  }
}

/** Strip sensitive keys from a `?a=1&token=…` search string (with or without `?`). */
export function scrubSensitiveSearch(search: string): string {
  if (!search) {
    return "";
  }
  const raw = search.startsWith("?") ? search.slice(1) : search;
  const params = new URLSearchParams(raw);
  scrubSearchParams(params);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

/** Scrub sensitive query keys from an in-app path (`/path?token=x#hash`). */
export function scrubSensitivePath(fullPath: string): string {
  try {
    const url = new URL(fullPath, "http://local.invalid");
    scrubSearchParams(url.searchParams);
    const qs = url.searchParams.toString();
    return `${url.pathname}${qs ? `?${qs}` : ""}${url.hash}`;
  } catch {
    return fullPath;
  }
}

/** Scrub sensitive query keys from an absolute or relative URL string. */
export function scrubSensitiveUrl(url: string): string {
  try {
    const parsed = new URL(
      url,
      typeof window !== "undefined" ? window.location.origin : "http://local.invalid",
    );
    scrubSearchParams(parsed.searchParams);
    if (/^https?:\/\//i.test(url.trim())) {
      return parsed.toString();
    }
    const qs = parsed.searchParams.toString();
    return `${parsed.pathname}${qs ? `?${qs}` : ""}${parsed.hash}`;
  } catch {
    return scrubSensitivePath(url);
  }
}
