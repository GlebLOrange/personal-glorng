import { ref, watch, type Ref } from "vue";

import { api } from "@/composables/useApi";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExpenseParseResult } from "@/types";

export function useExpenseParse(smartText: Ref<string>, defaultCurrency: Ref<CurrencyCode>) {
  const parsed = ref<ExpenseParseResult | null>(null);
  const parsing = ref(false);

  async function parseNow(text: string): Promise<void> {
    const trimmed = text.trim();
    if (!trimmed) {
      parsed.value = null;
      return;
    }

    parsing.value = true;
    try {
      const { data } = await api.post<ExpenseParseResult>("/tools/expenses/parse", {
        text: trimmed,
        default_currency: defaultCurrency.value,
      });
      parsed.value = data;
    } catch {
      parsed.value = { valid: false, error: "Failed to parse expense" };
    } finally {
      parsing.value = false;
    }
  }

  let debounceTimer: ReturnType<typeof setTimeout>;
  watch([smartText, defaultCurrency], () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => parseNow(smartText.value), 300);
  });

  return { parsed, parsing, parseNow };
}
