import { describe, expect, it } from "vitest";

import { EXPENSE_CURRENCIES, isCurrencyCode } from "@/constants/expenseCatalog";

describe("isCurrencyCode", () => {
  it("accepts catalog currencies case-insensitively", () => {
    for (const code of EXPENSE_CURRENCIES) {
      expect(isCurrencyCode(code)).toBe(true);
      expect(isCurrencyCode(code.toLowerCase())).toBe(true);
    }
  });

  it("rejects unknown codes", () => {
    expect(isCurrencyCode("XYZ")).toBe(false);
    expect(isCurrencyCode("")).toBe(false);
    expect(isCurrencyCode(null)).toBe(false);
  });
});
