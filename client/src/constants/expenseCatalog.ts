import catalog from "../../../shared/expense_catalog.json";

type ExpenseCatalogJson = {
  currencies: readonly string[];
  default_currency: string;
  exchange_rate_targets: readonly string[];
  categories: readonly string[];
  default_category: string;
};

const data = catalog as ExpenseCatalogJson;

export type CurrencyCode = (typeof data.currencies)[number];

export const EXPENSE_CURRENCIES = [...data.currencies] as CurrencyCode[];
export const EXPENSE_DEFAULT_CURRENCY = data.default_currency as CurrencyCode;
export const EXPENSE_EXCHANGE_RATE_TARGETS = [...data.exchange_rate_targets] as CurrencyCode[];
export const DEFAULT_EXPENSE_CATEGORIES = [...data.categories] as readonly string[];
export const DEFAULT_EXPENSE_CATEGORY = data.default_category;

/** True when value is an allowed expense currency code (case-insensitive). */
export function isCurrencyCode(value: string | null | undefined): value is CurrencyCode {
  if (!value) return false;
  const normalized = value.trim().toUpperCase();
  return (EXPENSE_CURRENCIES as readonly string[]).includes(normalized);
}
