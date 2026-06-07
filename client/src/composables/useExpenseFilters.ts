import { computed, ref, watch, type Ref } from "vue";

import {
  isValidDateRange,
  isValidMonthValue,
  isoDateLocal,
  monthDateBounds,
  monthValueLocal,
} from "@/utils/dates";

export type MonthPreset = "this_month" | "last_month" | "custom" | "range";
export type DateFilterMode = "month" | "range";
export type CurrencyCode = "USD" | "EUR" | "PLN" | "BYN";

export const EXPENSE_DEFAULT_CURRENCY: CurrencyCode = "PLN";
export const EXPENSE_CURRENCIES: CurrencyCode[] = ["PLN", "EUR", "USD", "BYN"];
export const EXPENSE_EXCHANGE_RATE_TARGETS: CurrencyCode[] = ["EUR", "USD", "BYN"];
export const EXPENSE_CURRENCY_STORAGE_KEY = "expense_default_currency";
export const EXPENSE_LAST_CATEGORY_STORAGE_KEY = "expense_last_category";

/** Cross-rate from USD-base API rates (units of `to` per 1 `from`). */
export function crossRate(
  rates: Record<string, string>,
  from: CurrencyCode,
  to: CurrencyCode,
): number {
  const toRate = parseFloat(rates[to]);
  const fromRate = parseFloat(rates[from]);
  if (!Number.isFinite(toRate) || !Number.isFinite(fromRate) || fromRate === 0) {
    return Number.NaN;
  }
  return toRate / fromRate;
}

export function useExpenseFilters(
  displayCurrency: Ref<CurrencyCode>,
  onFiltersChange: () => void | Promise<void>,
  onProductFilterChange: () => void | Promise<void>,
) {
  const monthPreset = ref<MonthPreset>("this_month");
  const dateFilterMode = ref<DateFilterMode>("month");
  const selectedMonth = ref("");
  const dateFrom = ref("");
  const dateTo = ref("");
  const productFilter = ref("");
  const categoryFilter = ref<string | null>(null);

  const monthLabel = computed(() => {
    if (dateFilterMode.value === "range" && dateFrom.value && dateTo.value) {
      const from = new Date(dateFrom.value + "T00:00:00");
      const to = new Date(dateTo.value + "T00:00:00");
      const fmt = (d: Date) =>
        d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
      return `${fmt(from)} – ${fmt(to)}`;
    }
    if (!selectedMonth.value) return "";
    const [year, month] = selectedMonth.value.split("-").map(Number);
    return new Date(year, month - 1, 1).toLocaleDateString("en-GB", {
      month: "long",
      year: "numeric",
    });
  });

  const hasActiveFilters = computed(
    () =>
      Boolean(productFilter.value.trim()) ||
      Boolean(categoryFilter.value) ||
      dateFilterMode.value === "range",
  );

  const rangeError = computed(() => {
    if (dateFilterMode.value !== "range") {
      return null;
    }
    if (!dateFrom.value || !dateTo.value) {
      return null;
    }
    if (!isValidDateRange(dateFrom.value, dateTo.value)) {
      return "End date must be on or after start date";
    }
    return null;
  });

  function applyMonthPreset(preset: MonthPreset): void {
    monthPreset.value = preset;
    const today = new Date();

    if (preset === "range") {
      dateFilterMode.value = "range";
      const start = new Date(today.getFullYear(), today.getMonth(), 1);
      dateFrom.value = isoDateLocal(start);
      dateTo.value = isoDateLocal(today);
      return;
    }

    dateFilterMode.value = "month";
    if (preset === "custom") return;

    if (preset === "this_month") {
      selectedMonth.value = monthValueLocal(today);
      return;
    }

    const prev = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    selectedMonth.value = monthValueLocal(prev);
  }

  function clearFilters(): void {
    productFilter.value = "";
    categoryFilter.value = null;
    applyMonthPreset("this_month");
  }

  function queryParams(): Record<string, string> {
    const params: Record<string, string> = {};

    if (dateFilterMode.value === "range") {
      if (dateFrom.value && dateTo.value && isValidDateRange(dateFrom.value, dateTo.value)) {
        params.date_from = dateFrom.value;
        params.date_to = dateTo.value;
      }
    } else if (selectedMonth.value && isValidMonthValue(selectedMonth.value)) {
      params.month = selectedMonth.value;
    }

    if (productFilter.value.trim()) {
      params.tool_name = productFilter.value.trim();
    }
    if (categoryFilter.value) params.category = categoryFilter.value;
    return params;
  }

  function summaryParams(): Record<string, string> {
    return { ...queryParams(), display_currency: displayCurrency.value };
  }

  /** Prior period with the same span (for month-over-month comparison). */
  function previousSummaryParams(): Record<string, string> {
    const params: Record<string, string> = {
      display_currency: displayCurrency.value,
    };

    if (dateFilterMode.value === "range" && dateFrom.value && dateTo.value) {
      const from = new Date(dateFrom.value + "T00:00:00");
      const to = new Date(dateTo.value + "T00:00:00");
      const spanDays = Math.max(0, Math.round((to.getTime() - from.getTime()) / 86_400_000));
      const prevEnd = new Date(from);
      prevEnd.setDate(prevEnd.getDate() - 1);
      const prevStart = new Date(prevEnd);
      prevStart.setDate(prevStart.getDate() - spanDays);
      params.date_from = isoDateLocal(prevStart);
      params.date_to = isoDateLocal(prevEnd);
      return params;
    }

    if (selectedMonth.value) {
      const [year, month] = selectedMonth.value.split("-").map(Number);
      const prev = new Date(year, month - 2, 1);
      params.month = monthValueLocal(prev);
    }

    return params;
  }

  let debounceTimer: ReturnType<typeof setTimeout>;
  watch(productFilter, () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(onProductFilterChange, 300);
  });

  watch([selectedMonth, categoryFilter, dateFrom, dateTo, dateFilterMode], onFiltersChange);

  watch(selectedMonth, (month) => {
    if (!month || dateFilterMode.value !== "month") return;
    const bounds = monthDateBounds(month);
    if (!bounds) return;
    dateFrom.value = bounds.from;
    dateTo.value = bounds.to;
  });

  return {
    monthPreset,
    dateFilterMode,
    selectedMonth,
    dateFrom,
    dateTo,
    productFilter,
    categoryFilter,
    monthLabel,
    hasActiveFilters,
    rangeError,
    applyMonthPreset,
    clearFilters,
    queryParams,
    summaryParams,
    previousSummaryParams,
  };
}
