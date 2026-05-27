import { ref, type Ref } from "vue";

import { api } from "@/composables/useApi";

const cache = new Map<string, { data: unknown; ts: number }>();
const DEFAULT_TTL_MS = 5 * 60 * 1000;

/**
 * Returns cached API data if still fresh, otherwise fetches and caches.
 * TTL defaults to 5 minutes.
 */
export function useCachedApi<T>(
  url: string,
  ttlMs: number = DEFAULT_TTL_MS,
): { data: Ref<T | null>; loading: Ref<boolean>; fetch: () => Promise<void> } {
  const data = ref<T | null>(null) as Ref<T | null>;
  const loading = ref(true);

  async function load(): Promise<void> {
    const cached = cache.get(url);
    if (cached && Date.now() - cached.ts < ttlMs) {
      data.value = cached.data as T;
      loading.value = false;
      return;
    }

    loading.value = true;
    try {
      const res = await api.get<T>(url);
      data.value = res.data;
      cache.set(url, { data: res.data, ts: Date.now() });
    } catch (err) {
      console.error(`[useCachedApi] ${url}`, err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return { data, loading, fetch: load };
}
