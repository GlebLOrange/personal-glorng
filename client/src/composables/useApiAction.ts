import { ref } from "vue";

import { getApiErrorMessage } from "@/types/api";

import { useNotify } from "./useNotify";

export interface ApiActionOptions {
  errorFallback?: string;
  successMessage?: string;
  silent?: boolean;
  logContext?: string;
}

/** Wrap async API calls with shared loading and error toast handling. */
export function useApiAction() {
  const loading = ref(false);
  const lastError = ref<string | null>(null);
  const { toast } = useNotify();

  async function run<T>(
    action: () => Promise<T>,
    options: ApiActionOptions = {},
  ): Promise<T | null> {
    loading.value = true;
    try {
      const result = await action();
      lastError.value = null;
      if (options.successMessage) {
        toast(options.successMessage, "success");
      }
      return result;
    } catch (err) {
      const message = getApiErrorMessage(err, options.errorFallback ?? "Request failed");
      lastError.value = message;
      console.error(options.logContext ?? "api", err);
      if (!options.silent) {
        toast(message, "error");
      }
      return null;
    } finally {
      loading.value = false;
    }
  }

  return { loading, lastError, run };
}
