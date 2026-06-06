/** Build absolute public URL for a short code path segment. */
export function publicUrl(pathSegment: string, code: string): string {
  const base = typeof window !== "undefined" ? window.location.origin : "";
  const path = pathSegment.startsWith("/") ? pathSegment : `/${pathSegment}`;
  return `${base}${path}/${code}`;
}
