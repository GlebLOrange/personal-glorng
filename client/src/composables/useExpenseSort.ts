import { computed, ref } from "vue";

import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ToolExpense } from "@/types";

export type ExpenseSortKey = "date" | "amount" | "category" | "product";
export type ExpenseSortDir = "asc" | "desc";

export function useExpenseSort(
  expenses: () => ToolExpense[],
  displayCurrency: () => CurrencyCode,
  convertAmount: (amount: string, from: CurrencyCode, to: CurrencyCode) => number,
) {
  const sortKey = ref<ExpenseSortKey>("date");
  const sortDir = ref<ExpenseSortDir>("desc");

  function toggleSort(key: ExpenseSortKey): void {
    if (sortKey.value === key) {
      sortDir.value = sortDir.value === "asc" ? "desc" : "asc";
      return;
    }
    sortKey.value = key;
    sortDir.value = key === "date" || key === "amount" ? "desc" : "asc";
  }

  const sortedExpenses = computed(() => {
    const items = [...expenses()];
    const dir = sortDir.value === "asc" ? 1 : -1;
    const currency = displayCurrency();

    items.sort((left, right) => {
      if (sortKey.value === "date") {
        return left.expense_date.localeCompare(right.expense_date) * dir;
      }
      if (sortKey.value === "amount") {
        const leftAmount = convertAmount(
          left.amount,
          left.currency as CurrencyCode,
          currency,
        );
        const rightAmount = convertAmount(
          right.amount,
          right.currency as CurrencyCode,
          currency,
        );
        return (leftAmount - rightAmount) * dir;
      }
      if (sortKey.value === "category") {
        return (left.category ?? "").localeCompare(right.category ?? "") * dir;
      }
      return left.tool_name.localeCompare(right.tool_name) * dir;
    });

    return items;
  });

  function sortIndicator(key: ExpenseSortKey): string {
    if (sortKey.value !== key) return "";
    return sortDir.value === "asc" ? " ↑" : " ↓";
  }

  return { sortKey, sortDir, sortedExpenses, toggleSort, sortIndicator };
}
