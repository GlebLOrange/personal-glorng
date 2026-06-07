import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import { getApiErrorMessage } from "@/types/api";
import type { BaseChatConfig } from "@/types/search";

interface UseChatConfigOptions<T extends BaseChatConfig> {
  path: string;
  fallback: T;
  onError?: (message: string) => void;
}

export function useChatConfig<T extends BaseChatConfig>(options: UseChatConfigOptions<T>) {
  const config = ref<T | null>(null);
  const loading = ref(true);

  async function loadConfig(): Promise<void> {
    loading.value = true;
    try {
      const { data } = await api.get<T>(options.path);
      config.value = data;
    } catch (err) {
      config.value = options.fallback;
      options.onError?.(getApiErrorMessage(err, "Failed to load chat config"));
    } finally {
      loading.value = false;
    }
  }

  const isReady = computed(
    () => Boolean(config.value?.enabled && config.value?.configured),
  );

  return {
    config,
    loading,
    loadConfig,
    isReady,
  };
}
