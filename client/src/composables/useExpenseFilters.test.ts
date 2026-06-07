import { nextTick, ref } from "vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  crossRate,
  EXPENSE_EXCHANGE_RATE_TARGETS,
  useExpenseFilters,
} from "@/composables/useExpenseFilters";

describe("useExpenseFilters", () => {
  const onFiltersChange = vi.fn();
  const onProductFilterChange = vi.fn();
  const displayCurrency = ref<"PLN">("PLN");

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    vi.setSystemTime(new Date(2026, 5, 6));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("sets this_month on applyMonthPreset", () => {
    const { selectedMonth, applyMonthPreset } = useExpenseFilters(
      displayCurrency,
      onFiltersChange,
      onProductFilterChange,
    );
    applyMonthPreset("this_month");

    expect(selectedMonth.value).toBe("2026-06");
  });

  it("sets last_month on applyMonthPreset", () => {
    const { selectedMonth, applyMonthPreset } = useExpenseFilters(
      displayCurrency,
      onFiltersChange,
      onProductFilterChange,
    );
    applyMonthPreset("last_month");

    expect(selectedMonth.value).toBe("2026-05");
  });

  it("builds queryParams with month, product, and category", () => {
    const { selectedMonth, productFilter, categoryFilter, queryParams, applyMonthPreset } =
      useExpenseFilters(displayCurrency, onFiltersChange, onProductFilterChange);

    applyMonthPreset("this_month");
    productFilter.value = "  milk  ";
    categoryFilter.value = "food";

    expect(queryParams()).toEqual({
      month: selectedMonth.value,
      tool_name: "milk",
      category: "food",
    });
  });

  it("omits inverted date range from queryParams and sets rangeError", () => {
    const { dateFrom, dateTo, queryParams, rangeError, applyMonthPreset } = useExpenseFilters(
      displayCurrency,
      onFiltersChange,
      onProductFilterChange,
    );

    applyMonthPreset("range");
    dateFrom.value = "2026-06-10";
    dateTo.value = "2026-06-01";

    expect(rangeError.value).toBe("End date must be on or after start date");
    expect(queryParams()).toEqual({});
  });

  it("builds queryParams with date range", () => {
    const { queryParams, applyMonthPreset, dateFilterMode } = useExpenseFilters(
      displayCurrency,
      onFiltersChange,
      onProductFilterChange,
    );

    applyMonthPreset("range");

    expect(dateFilterMode.value).toBe("range");
    expect(queryParams()).toEqual({
      date_from: "2026-06-01",
      date_to: "2026-06-06",
    });
  });

  it("includes display_currency in summaryParams", () => {
    const { summaryParams, applyMonthPreset } = useExpenseFilters(
      displayCurrency,
      onFiltersChange,
      onProductFilterChange,
    );
    applyMonthPreset("this_month");

    expect(summaryParams()).toMatchObject({
      month: "2026-06",
      display_currency: "PLN",
    });
  });

  it("builds previousSummaryParams for prior month", () => {
    const { applyMonthPreset, previousSummaryParams } = useExpenseFilters(
      displayCurrency,
      onFiltersChange,
      onProductFilterChange,
    );

    applyMonthPreset("this_month");

    expect(previousSummaryParams()).toEqual({
      month: "2026-05",
      display_currency: "PLN",
    });
  });

  it("clears filters back to this month", () => {
    const { productFilter, categoryFilter, clearFilters, applyMonthPreset, monthPreset } =
      useExpenseFilters(displayCurrency, onFiltersChange, onProductFilterChange);

    applyMonthPreset("range");
    productFilter.value = "coffee";
    categoryFilter.value = "Groceries";
    clearFilters();

    expect(productFilter.value).toBe("");
    expect(categoryFilter.value).toBeNull();
    expect(monthPreset.value).toBe("this_month");
  });

  it("debounces product filter changes", async () => {
    const { productFilter } = useExpenseFilters(
      displayCurrency,
      onFiltersChange,
      onProductFilterChange,
    );

    productFilter.value = "a";
    await nextTick();
    productFilter.value = "ab";
    await nextTick();
    await vi.advanceTimersByTimeAsync(300);

    expect(onProductFilterChange).toHaveBeenCalledTimes(1);
  });
});

describe("expense currency constants", () => {
  const sampleRates = {
    USD: "1",
    EUR: "0.92",
    PLN: "4.0",
    BYN: "3.28",
  };

  it("orders exchange rate targets as EUR, USD, BYN", () => {
    expect(EXPENSE_EXCHANGE_RATE_TARGETS).toEqual(["EUR", "USD", "BYN"]);
  });

  it("computes crossRate from USD-base rates", () => {
    expect(crossRate(sampleRates, "PLN", "EUR")).toBeCloseTo(0.23, 4);
    expect(crossRate(sampleRates, "PLN", "USD")).toBeCloseTo(0.25, 4);
    expect(crossRate(sampleRates, "PLN", "BYN")).toBeCloseTo(0.82, 4);
  });
});
