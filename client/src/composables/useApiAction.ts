import { ref, type Ref } from "vue";

import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import type { Toast } from "@/types";

type ApiActionOptions = {
  errorMessage?: string;
  /** Alias for errorMessage used by some admin tools. */
  errorFallback?: string;
  successMessage?: string;
  successType?: Toast["type"];
  logErrors?: boolean;
};

/** Run async API work with loading state and consistent error toasts. */
export function useApiAction(defaultOptions: ApiActionOptions = {}) {
  const loading = ref(false);
  const { toast } = useNotify();

  async function run<T>(
    action: () => Promise<T>,
    options: ApiActionOptions = {},
  ): Promise<T | undefined> {
    const merged = { ...defaultOptions, ...options };
    loading.value = true;
    try {
      const result = await action();
      if (merged.successMessage) {
        toast(merged.successMessage, merged.successType ?? "success");
      }
      return result;
    } catch (err) {
      if (merged.logErrors !== false && import.meta.env.DEV) {
        console.error(err);
      }
      const fallback = merged.errorMessage ?? merged.errorFallback ?? "Request failed";
      const message = getApiErrorMessage(err, fallback);
      toast(message, "error");
      return undefined;
    } finally {
      loading.value = false;
    }
  }

  return { loading, run } as { loading: Ref<boolean>; run: typeof run };
}
