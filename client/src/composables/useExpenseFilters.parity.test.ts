import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  DEFAULT_EXPENSE_CATEGORIES,
  DEFAULT_EXPENSE_CATEGORY,
} from "@/constants/expenseCategories";
import {
  EXPENSE_CURRENCIES,
  EXPENSE_DEFAULT_CURRENCY,
  EXPENSE_EXCHANGE_RATE_TARGETS,
} from "@/composables/useExpenseFilters";

const catalogPath = resolve(__dirname, "../../../shared/expense_catalog.json");

describe("expense catalog parity", () => {
  it("matches shared expense_catalog.json", () => {
    const fixture = JSON.parse(readFileSync(catalogPath, "utf-8")) as {
      currencies: string[];
      default_currency: string;
      exchange_rate_targets: string[];
      categories: string[];
      default_category: string;
    };

    expect(EXPENSE_CURRENCIES).toEqual(fixture.currencies);
    expect(EXPENSE_DEFAULT_CURRENCY).toBe(fixture.default_currency);
    expect(EXPENSE_EXCHANGE_RATE_TARGETS).toEqual(fixture.exchange_rate_targets);
    expect([...DEFAULT_EXPENSE_CATEGORIES]).toEqual(fixture.categories);
    expect(DEFAULT_EXPENSE_CATEGORY).toBe(fixture.default_category);
  });
});
