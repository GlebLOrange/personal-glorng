import type { CurrencyCode } from "@/composables/useExpenseFilters";
import {
  crossRate,
  EXPENSE_CURRENCIES,
  EXPENSE_DEFAULT_CURRENCY,
  EXPENSE_EXCHANGE_RATE_TARGETS,
} from "@/composables/useExpenseFilters";
import { api } from "@/composables/useApi";
import type { ExchangeRates } from "@/types";

export interface ConvertResult {
  amount: string;
  from_currency: CurrencyCode;
  to_currency: CurrencyCode;
  converted: string;
  rates_updated_at: string | null;
}

export function formatMoney(value: string | number, currency: string): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (!Number.isFinite(num)) return "N/A";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(num);
}

export function formatRate(
  rates: Record<string, string> | null | undefined,
  from: CurrencyCode,
  to: CurrencyCode,
): string {
  if (!rates) return "N/A";
  const rate = crossRate(rates, from, to);
  return Number.isFinite(rate) ? rate.toFixed(4) : "N/A";
}

export async function fetchExchangeRates(): Promise<ExchangeRates | null> {
  try {
    const { data } = await api.get<ExchangeRates>("/tools/expense-calculator/rates");
    return data;
  } catch {
    return null;
  }
}

export async function convertCurrency(
  amount: number,
  fromCurrency: CurrencyCode,
  toCurrency: CurrencyCode,
): Promise<ConvertResult | null> {
  if (!Number.isFinite(amount) || amount <= 0) return null;
  try {
    const { data } = await api.post<ConvertResult>("/tools/expense-calculator/convert", {
      amount: amount.toFixed(2),
      from_currency: fromCurrency,
      to_currency: toCurrency,
    });
    return data;
  } catch {
    return null;
  }
}

export {
  crossRate,
  EXPENSE_CURRENCIES,
  EXPENSE_DEFAULT_CURRENCY,
  EXPENSE_EXCHANGE_RATE_TARGETS,
};
