import { ref, toValue, type MaybeRefOrGetter, type Ref } from "vue";

import { api } from "@/composables/useApi";

const cache = new Map<string, { data: unknown; ts: number }>();
const DEFAULT_TTL_MS = 5 * 60 * 1000;
const MAX_CACHE_ENTRIES = 64;

function pruneCache(ttlMs: number): void {
  const now = Date.now();
  for (const [key, entry] of cache) {
    if (now - entry.ts >= ttlMs) {
      cache.delete(key);
    }
  }
  if (cache.size <= MAX_CACHE_ENTRIES) {
    return;
  }
  const sorted = [...cache.entries()].sort((a, b) => a[1].ts - b[1].ts);
  const excess = cache.size - MAX_CACHE_ENTRIES;
  for (let i = 0; i < excess; i += 1) {
    cache.delete(sorted[i][0]);
  }
}

/**
 * Returns cached API data if still fresh, otherwise fetches and caches.
 * TTL defaults to 5 minutes.
 */
export function useCachedApi<T>(
  url: MaybeRefOrGetter<string>,
  ttlMs: number = DEFAULT_TTL_MS,
): { data: Ref<T | null>; loading: Ref<boolean>; fetch: () => Promise<void> } {
  const data = ref<T | null>(null) as Ref<T | null>;
  const loading = ref(true);
  let generation = 0;

  async function load(): Promise<void> {
    const resolved = toValue(url);
    const requestGen = ++generation;

    const cached = cache.get(resolved);
    if (cached && Date.now() - cached.ts < ttlMs) {
      if (requestGen === generation) {
        data.value = cached.data as T;
        loading.value = false;
      }
      return;
    }
    if (cached) {
      cache.delete(resolved);
    }

    loading.value = true;
    try {
      const res = await api.get<T>(resolved);
      if (requestGen !== generation) {
        return;
      }
      data.value = res.data;
      cache.set(resolved, { data: res.data, ts: Date.now() });
      pruneCache(ttlMs);
    } catch (err) {
      if (requestGen !== generation) {
        return;
      }
      console.error(`[useCachedApi] ${resolved}`, err);
      throw err;
    } finally {
      if (requestGen === generation) {
        loading.value = false;
      }
    }
  }

  return { data, loading, fetch: load };
}

/** Drop a cached entry so the next fetch hits the network. */
export function invalidateCachedApi(url: string): void {
  cache.delete(url);
}
