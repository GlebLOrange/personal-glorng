import {
  EXPENSE_CURRENCIES,
  EXPENSE_DEFAULT_CURRENCY,
  type CurrencyCode,
} from "@/composables/useExpenseFilters";

export const EXPENSE_CONVERTER_STORAGE_KEY = "expense_converter_last";

export type ExpenseConverterSnapshot = {
  amount: string;
  fromCurrency: CurrencyCode;
  toCurrency: CurrencyCode;
};

const DEFAULT_SNAPSHOT: ExpenseConverterSnapshot = {
  amount: "100",
  fromCurrency: "EUR",
  toCurrency: EXPENSE_DEFAULT_CURRENCY,
};

function isCurrencyCode(value: unknown): value is CurrencyCode {
  return typeof value === "string" && EXPENSE_CURRENCIES.includes(value as CurrencyCode);
}

/** Validate persisted converter state; fall back to defaults on any bad shape. */
export function sanitizeConverterSnapshot(raw: unknown): ExpenseConverterSnapshot {
  if (!raw || typeof raw !== "object") return { ...DEFAULT_SNAPSHOT };
  const record = raw as Record<string, unknown>;
  const amountRaw =
    typeof record.amount === "string"
      ? record.amount.trim()
      : typeof record.amount === "number"
        ? String(record.amount)
        : "";
  const amountNum = parseFloat(amountRaw);
  const amount =
    amountRaw && Number.isFinite(amountNum) && amountNum > 0 ? amountRaw : DEFAULT_SNAPSHOT.amount;
  const fromCurrency = isCurrencyCode(record.fromCurrency)
    ? record.fromCurrency
    : DEFAULT_SNAPSHOT.fromCurrency;
  const toCurrency = isCurrencyCode(record.toCurrency)
    ? record.toCurrency
    : DEFAULT_SNAPSHOT.toCurrency;
  return { amount, fromCurrency, toCurrency };
}

export function readConverterSnapshot(): ExpenseConverterSnapshot {
  if (typeof localStorage === "undefined") return { ...DEFAULT_SNAPSHOT };
  try {
    const raw = localStorage.getItem(EXPENSE_CONVERTER_STORAGE_KEY);
    if (raw === null) return { ...DEFAULT_SNAPSHOT };
    return sanitizeConverterSnapshot(JSON.parse(raw));
  } catch {
    return { ...DEFAULT_SNAPSHOT };
  }
}

export function writeConverterSnapshot(snapshot: ExpenseConverterSnapshot): void {
  if (typeof localStorage === "undefined") return;
  try {
    const normalized = sanitizeConverterSnapshot(snapshot);
    localStorage.setItem(EXPENSE_CONVERTER_STORAGE_KEY, JSON.stringify(normalized));
  } catch {
    // ignore quota / private mode
  }
}
