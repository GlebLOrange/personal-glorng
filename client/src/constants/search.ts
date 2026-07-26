/** Minimum trimmed length before a search query is sent to the API. */
export const SEARCH_MIN_QUERY_LENGTH = 3;

/**
 * Trimmed query ready to send, or `undefined` if empty / below the minimum.
 * Empty and 1–2 character inputs both mean "no search filter".
 */
export function effectiveSearchQuery(raw: string): string | undefined {
  const q = raw.trim();
  if (q.length >= SEARCH_MIN_QUERY_LENGTH) return q;
  return undefined;
}
