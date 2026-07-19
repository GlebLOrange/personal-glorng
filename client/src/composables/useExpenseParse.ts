import { onUnmounted, ref, watch, type Ref } from "vue";

import { api } from "@/composables/useApi";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExpenseParseResult } from "@/types";

export function useExpenseParse(smartText: Ref<string>, defaultCurrency: Ref<CurrencyCode>) {
  const parsed = ref<ExpenseParseResult | null>(null);
  const parsing = ref(false);
  let requestId = 0;

  async function parseNow(text: string): Promise<void> {
    const trimmed = text.trim();
    if (!trimmed) {
      requestId += 1;
      parsed.value = null;
      parsing.value = false;
      return;
    }

    const id = ++requestId;
    parsing.value = true;
    try {
      const { data } = await api.post<ExpenseParseResult>("/tools/expenses/parse", {
        text: trimmed,
        default_currency: defaultCurrency.value,
      });
      if (id !== requestId) return;
      parsed.value = data;
    } catch {
      if (id !== requestId) return;
      parsed.value = { valid: false, error: "Failed to parse expense" };
    } finally {
      if (id === requestId) parsing.value = false;
    }
  }

  let debounceTimer: ReturnType<typeof setTimeout> | undefined;
  watch([smartText, defaultCurrency], () => {
    clearTimeout(debounceTimer);
    // Invalidate immediately so confirm cannot use a stale parse during debounce / in-flight.
    requestId += 1;
    parsed.value = null;
    const pending = Boolean(smartText.value.trim());
    parsing.value = pending;
    debounceTimer = setTimeout(() => parseNow(smartText.value), 300);
  });

  onUnmounted(() => {
    clearTimeout(debounceTimer);
    requestId += 1;
  });

  return { parsed, parsing, parseNow };
}
