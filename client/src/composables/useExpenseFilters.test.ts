import { nextTick, ref } from "vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useExpenseFilters } from "@/composables/useExpenseFilters";

describe("useExpenseFilters", () => {
  const onFiltersChange = vi.fn();
  const onProductFilterChange = vi.fn();
  const displayCurrency = ref<"PLN">("PLN");

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("sets this_month on applyMonthPreset", () => {
    const now = new Date(2026, 4, 15);
    vi.setSystemTime(now);

    const { selectedMonth, applyMonthPreset } = useExpenseFilters(
      displayCurrency,
      onFiltersChange,
      onProductFilterChange,
    );
    applyMonthPreset("this_month");

    expect(selectedMonth.value).toBe("2026-05");
  });

  it("sets last_month on applyMonthPreset", () => {
    vi.setSystemTime(new Date(2026, 0, 10));

    const { selectedMonth, applyMonthPreset } = useExpenseFilters(
      displayCurrency,
      onFiltersChange,
      onProductFilterChange,
    );
    applyMonthPreset("last_month");

    expect(selectedMonth.value).toBe("2025-12");
  });

  it("builds queryParams with month, product, and category", () => {
    vi.setSystemTime(new Date(2026, 4, 1));

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

  it("includes display_currency in summaryParams", () => {
    const { summaryParams, applyMonthPreset } = useExpenseFilters(
      displayCurrency,
      onFiltersChange,
      onProductFilterChange,
    );
    applyMonthPreset("this_month");

    expect(summaryParams()).toMatchObject({
      month: "2026-05",
      display_currency: "PLN",
    });
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
