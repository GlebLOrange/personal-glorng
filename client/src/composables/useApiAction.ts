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
  /** Skip error toast (caller handles or failure is non-critical). */
  silent?: boolean;
  /** DEV-only context label for console.error. */
  logContext?: string;
};

/** Run async API work with loading state and consistent error toasts. */
export function useApiAction(defaultOptions: ApiActionOptions = {}) {
  const loading = ref(false);
  const lastError = ref<string | null>(null);
  const { toast } = useNotify();

  async function run<T>(
    action: () => Promise<T>,
    options: ApiActionOptions = {},
  ): Promise<T | undefined> {
    const merged = { ...defaultOptions, ...options };
    loading.value = true;
    try {
      const result = await action();
      lastError.value = null;
      if (merged.successMessage) {
        toast(merged.successMessage, merged.successType ?? "success");
      }
      return result;
    } catch (err) {
      const fallback = merged.errorMessage ?? merged.errorFallback ?? "Request failed";
      const message = getApiErrorMessage(err, fallback);
      lastError.value = message;
      if (merged.logErrors !== false && import.meta.env.DEV) {
        const prefix = merged.logContext ? `[${merged.logContext}] ` : "";
        console.error(`${prefix}${message}`, err);
      }
      if (!merged.silent) {
        toast(message, "error");
      }
      return undefined;
    } finally {
      loading.value = false;
    }
  }

  return { loading, lastError, run } as {
    loading: Ref<boolean>;
    lastError: Ref<string | null>;
    run: typeof run;
  };
}
