import { describe, expect, it } from "vitest";

import {
  isCalculatorMode,
  normalizeCalculatorMode,
} from "@/composables/useExpenseCalculator";

describe("normalizeCalculatorMode", () => {
  it("maps converter alias to convert", () => {
    expect(normalizeCalculatorMode("converter")).toBe("convert");
  });

  it("passes through known calculator modes", () => {
    expect(normalizeCalculatorMode("convert")).toBe("convert");
    expect(normalizeCalculatorMode("sum")).toBe("sum");
    expect(normalizeCalculatorMode("budget")).toBe("budget");
    expect(normalizeCalculatorMode("whatif")).toBe("whatif");
  });

  it("defaults unknown values to convert", () => {
    expect(normalizeCalculatorMode("transactions")).toBe("convert");
    expect(normalizeCalculatorMode("")).toBe("convert");
  });
});

describe("isCalculatorMode", () => {
  it("accepts calculator modes only", () => {
    expect(isCalculatorMode("convert")).toBe(true);
    expect(isCalculatorMode("whatif")).toBe(true);
    expect(isCalculatorMode("converter")).toBe(false);
    expect(isCalculatorMode("transactions")).toBe(false);
  });
});
