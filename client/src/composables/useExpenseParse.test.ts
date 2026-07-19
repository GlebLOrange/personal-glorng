import { nextTick, ref } from "vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "@/composables/useApi";
import { useExpenseParse } from "@/composables/useExpenseParse";
import type { CurrencyCode } from "@/composables/useExpenseFilters";

vi.mock("@/composables/useApi", () => ({
  api: {
    post: vi.fn(),
  },
}));

describe("useExpenseParse", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("ignores stale parse responses", async () => {
    let resolveFirst: ((value: { data: unknown }) => void) | undefined;
    let resolveSecond: ((value: { data: unknown }) => void) | undefined;

    vi.mocked(api.post)
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            resolveFirst = resolve;
          }),
      )
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            resolveSecond = resolve;
          }),
      );

    const smartText = ref("coffee 10");
    const defaultCurrency = ref<CurrencyCode>("PLN");
    const { parsed, parseNow } = useExpenseParse(smartText, defaultCurrency);

    const first = parseNow("coffee 10");
    const second = parseNow("lunch 25");

    resolveSecond?.({
      data: { valid: true, amount: 25, description: "lunch" },
    });
    await second;

    resolveFirst?.({
      data: { valid: true, amount: 10, description: "coffee" },
    });
    await first;
    await nextTick();

    expect(parsed.value).toEqual({ valid: true, amount: 25, description: "lunch" });
  });

  it("debounced watch only keeps the latest parse", async () => {
    vi.mocked(api.post).mockResolvedValue({
      data: { valid: true, amount: 42, description: "tea" },
    });

    const smartText = ref("");
    const defaultCurrency = ref<CurrencyCode>("PLN");
    const { parsed } = useExpenseParse(smartText, defaultCurrency);

    smartText.value = "a";
    smartText.value = "tea 42";
    await vi.advanceTimersByTimeAsync(300);
    await nextTick();

    expect(api.post).toHaveBeenCalledTimes(1);
    expect(api.post).toHaveBeenCalledWith("/tools/expenses/parse", {
      text: "tea 42",
      default_currency: "PLN",
    });
    expect(parsed.value).toEqual({ valid: true, amount: 42, description: "tea" });
  });

  it("clears parsed immediately when text changes so confirm cannot use a stale result", async () => {
    vi.mocked(api.post).mockResolvedValue({
      data: { valid: true, amount: "10", tool_name: "Coffee" },
    });

    const smartText = ref("");
    const defaultCurrency = ref<CurrencyCode>("PLN");
    const { parsed, parsing } = useExpenseParse(smartText, defaultCurrency);

    smartText.value = "10 coffee";
    await vi.advanceTimersByTimeAsync(300);
    await nextTick();
    expect(parsed.value).toEqual({ valid: true, amount: "10", tool_name: "Coffee" });
    expect(parsing.value).toBe(false);

    smartText.value = "100 rent";
    await nextTick();
    expect(parsed.value).toBeNull();
    expect(parsing.value).toBe(true);

    vi.mocked(api.post).mockResolvedValue({
      data: { valid: true, amount: "100", tool_name: "Rent" },
    });
    await vi.advanceTimersByTimeAsync(300);
    await nextTick();
    expect(parsed.value).toEqual({ valid: true, amount: "100", tool_name: "Rent" });
    expect(parsing.value).toBe(false);
  });
});
