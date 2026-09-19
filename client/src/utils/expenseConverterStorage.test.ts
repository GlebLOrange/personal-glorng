import { describe, expect, it } from "vitest";

import {
  sanitizeConverterSnapshot,
} from "@/utils/expenseConverterStorage";

describe("sanitizeConverterSnapshot", () => {
  it("keeps a valid amount and currency pair", () => {
    expect(
      sanitizeConverterSnapshot({
        amount: "42.5",
        fromCurrency: "USD",
        toCurrency: "PLN",
      }),
    ).toEqual({
      amount: "42.5",
      fromCurrency: "USD",
      toCurrency: "PLN",
    });
  });

  it("falls back on invalid amount or currencies", () => {
    expect(sanitizeConverterSnapshot({ amount: "0", fromCurrency: "XYZ", toCurrency: 1 })).toEqual({
      amount: "100",
      fromCurrency: "EUR",
      toCurrency: "PLN",
    });
  });

  it("accepts numeric amounts from number inputs", () => {
    expect(
      sanitizeConverterSnapshot({
        amount: 50,
        fromCurrency: "USD",
        toCurrency: "EUR",
      }),
    ).toEqual({
      amount: "50",
      fromCurrency: "USD",
      toCurrency: "EUR",
    });
  });

  it("falls back on non-object input", () => {
    expect(sanitizeConverterSnapshot(null)).toEqual({
      amount: "100",
      fromCurrency: "EUR",
      toCurrency: "PLN",
    });
  });
});
