import type { LocationQuery, Router } from "vue-router";

/** Copy query without the given keys (used after consuming one-time tokens). */
export function omitQueryKeys(query: LocationQuery, keys: string[]): LocationQuery {
  const next: LocationQuery = { ...query };
  for (const key of keys) {
    delete next[key];
  }
  return next;
}

/** Read a string query param and strip listed keys from the URL via replace. */
export async function consumeQueryParams(
  router: Router,
  path: string,
  query: LocationQuery,
  keys: string[],
): Promise<Record<string, string | undefined>> {
  const values: Record<string, string | undefined> = {};
  let shouldReplace = false;
  for (const key of keys) {
    const raw = query[key];
    values[key] = typeof raw === "string" ? raw : undefined;
    if (key in query) {
      shouldReplace = true;
    }
  }
  if (shouldReplace) {
    await router.replace({ path, query: omitQueryKeys(query, keys) });
  }
  return values;
}
