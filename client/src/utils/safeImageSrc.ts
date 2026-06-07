const BLOCKED_PROTOCOLS = new Set(["javascript:", "data:", "vbscript:", "blob:"]);

/** Allow https absolute URLs and same-origin relative paths for img src. */
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
    if (parsed.protocol === "https:") {
      return parsed.href;
    }
  } catch {
    return null;
  }

  return null;
}
