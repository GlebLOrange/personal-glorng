import { computed, ref, watch, type Ref } from "vue";

export type MonthPreset = "this_month" | "last_month" | "custom";
export type CurrencyCode = "USD" | "EUR" | "PLN" | "BYN";

export const EXPENSE_CURRENCIES: CurrencyCode[] = ["USD", "EUR", "PLN", "BYN"];
export const EXPENSE_CURRENCY_STORAGE_KEY = "expense_default_currency";

function currentMonthValue(d = new Date()): string {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  return `${year}-${month}`;
}

export function useExpenseFilters(
  displayCurrency: Ref<CurrencyCode>,
  onFiltersChange: () => void | Promise<void>,
  onProductFilterChange: () => void | Promise<void>,
) {
  const monthPreset = ref<MonthPreset>("this_month");
  const selectedMonth = ref("");
  const productFilter = ref("");
  const categoryFilter = ref<string | null>(null);

  const monthLabel = computed(() => {
    if (!selectedMonth.value) return "";
    const [year, month] = selectedMonth.value.split("-").map(Number);
    return new Date(year, month - 1, 1).toLocaleDateString("en-GB", {
      month: "long",
      year: "numeric",
    });
  });

  function applyMonthPreset(preset: MonthPreset): void {
    monthPreset.value = preset;
    if (preset === "custom") return;

    const today = new Date();
    if (preset === "this_month") {
      selectedMonth.value = currentMonthValue(today);
      return;
    }

    const prev = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    selectedMonth.value = currentMonthValue(prev);
  }

  function queryParams(): Record<string, string> {
    const params: Record<string, string> = {};
    if (selectedMonth.value) params.month = selectedMonth.value;
    if (productFilter.value.trim()) {
      params.tool_name = productFilter.value.trim();
    }
    if (categoryFilter.value) params.category = categoryFilter.value;
    return params;
  }

  function summaryParams(): Record<string, string> {
    return { ...queryParams(), display_currency: displayCurrency.value };
  }

  let debounceTimer: ReturnType<typeof setTimeout>;
  watch(productFilter, () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(onProductFilterChange, 300);
  });

  watch([selectedMonth, categoryFilter], onFiltersChange);

  return {
    monthPreset,
    selectedMonth,
    productFilter,
    categoryFilter,
    monthLabel,
    applyMonthPreset,
    queryParams,
    summaryParams,
  };
}
