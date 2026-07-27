/** Prefer content hub; otherwise first available category. */
export function defaultToolsCategory(available: readonly string[]): string {
  if (available.includes("content")) return "content";
  return available[0] ?? "";
}

/** Resolve ?category= against non-empty hub categories. */
export function resolveToolsCategory(
  queryValue: unknown,
  available: readonly string[],
): string {
  if (typeof queryValue === "string" && available.includes(queryValue)) {
    return queryValue;
  }
  return defaultToolsCategory(available);
}
