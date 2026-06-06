import { ref } from "vue";

import { getApiErrorMessage } from "@/types/api";

import { useNotify } from "./useNotify";

export interface ApiActionOptions {
  errorFallback?: string;
  successMessage?: string;
  silent?: boolean;
}

/** Wrap async API calls with shared loading and error toast handling. */
export function useApiAction() {
  const loading = ref(false);
  const { toast } = useNotify();

  async function run<T>(
    action: () => Promise<T>,
    options: ApiActionOptions = {},
  ): Promise<T | null> {
    loading.value = true;
    try {
      const result = await action();
      if (options.successMessage) {
        toast(options.successMessage, "success");
      }
      return result;
    } catch (err) {
      console.error(err);
      if (!options.silent) {
        toast(getApiErrorMessage(err, options.errorFallback ?? "Request failed"), "error");
      }
      return null;
    } finally {
      loading.value = false;
    }
  }

  return { loading, run };
}
