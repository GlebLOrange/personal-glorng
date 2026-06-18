import { computed, ref } from "vue";

export type ExpenseSortKey = "date" | "amount" | "category" | "product";
export type ExpenseSortDir = "asc" | "desc";

export function useExpenseSort() {
  const sortKey = ref<ExpenseSortKey>("date");
  const sortDir = ref<ExpenseSortDir>("desc");
  const sortParam = computed(() => `${sortKey.value}_${sortDir.value}`);

  function toggleSort(key: ExpenseSortKey): void {
    if (sortKey.value === key) {
      sortDir.value = sortDir.value === "asc" ? "desc" : "asc";
      return;
    }
    sortKey.value = key;
    sortDir.value = key === "date" || key === "amount" ? "desc" : "asc";
  }

  function sortIndicator(key: ExpenseSortKey): string {
    if (sortKey.value !== key) return "";
    return sortDir.value === "asc" ? " ↑" : " ↓";
  }

  return { sortKey, sortDir, sortParam, toggleSort, sortIndicator };
}
