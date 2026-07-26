import { computed, nextTick, ref, shallowRef, watch, type ComputedRef, type Ref } from "vue";

import { DEFAULT_EXPENSE_CATEGORY } from "@/constants/expenseCategories";
import { LIST_PAGE_SIZE } from "@/constants/pagination";
import {
  EXPENSE_CURRENCIES,
  EXPENSE_DEFAULT_CURRENCY,
  EXPENSE_LAST_CATEGORY_STORAGE_KEY,
  useExpenseFilters,
  type CurrencyCode,
  type MonthPreset,
} from "@/composables/useExpenseFilters";
import { useExpenseSort, type ExpenseSortKey } from "@/composables/useExpenseSort";
import { useExpenseSummary } from "@/composables/useExpenseSummary";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useLocalStorageString } from "@/composables/useLocalStorage";
import { useNotify } from "@/composables/useNotify";
import { isoDateLocal } from "@/utils/dates";
import type { Expense } from "@/types";

/** Focus/clear hooks for the expenses quick-add entry (QuickAdd or a wrapping panel). */
export type ExpenseQuickAddTarget = {
  focusEntry: () => void;
  focusSmartText: () => void;
  clearSmartText: () => void;
};

export type UseExpenseTransactionsOptions = {
  quickAddRef: Ref<ExpenseQuickAddTarget | null>;
  activeTab: Ref<string>;
  switchTab: (tab: string) => void;
  displayCurrency: Ref<CurrencyCode>;
  saveDisplayCurrency: (currency: CurrencyCode) => void | Promise<void>;
  categoryOptions: ComputedRef<string[]>;
  defaultCategoryName: ComputedRef<string>;
  loadCategories: () => Promise<void>;
};

/** List, filters, sort, pagination, form/quick-add, and expense CRUD/export. */
export function useExpenseTransactions(options: UseExpenseTransactionsOptions) {
  const {
    quickAddRef,
    activeTab,
    switchTab,
    displayCurrency,
    saveDisplayCurrency,
    categoryOptions,
    defaultCategoryName,
    loadCategories,
  } = options;

  const { run: runSaveExpense, loading: savingExpense } = useApiAction();
  const { run: runExport, loading: exporting } = useApiAction();
  const { run: runDeleteExpense, loading: deletingExpense } = useApiAction();
  const smartTextOpen = ref(false);
  const filtersOpen = ref(false);
  const showForm = ref(false);
  const editingId = ref<number | null>(null);
  const deleteTargetId = ref<number | null>(null);
  const expensePage = ref(1);

  const { value: lastCategory, set: setLastCategory } = useLocalStorageString(
    EXPENSE_LAST_CATEGORY_STORAGE_KEY,
    DEFAULT_EXPENSE_CATEGORY,
  );

  const filtersRef = shallowRef<ReturnType<typeof useExpenseFilters> | null>(null);
  const { sortParam, toggleSort, sortIndicator, sortAriaSort } = useExpenseSort();

  function expenseQueryParams(): Record<string, string> {
    return {
      ...(filtersRef.value?.queryParams() ?? {}),
      page: String(expensePage.value),
      per_page: String(LIST_PAGE_SIZE),
      sort: sortParam.value,
    };
  }

  const summaryHook = useExpenseSummary(
    expenseQueryParams,
    () => filtersRef.value?.summaryParams() ?? {},
    () => filtersRef.value?.previousSummaryParams() ?? {},
  );

  const {
    expenses,
    expenseTotal,
    expensePages,
    summary,
    periodChange,
    exchangeRates,
    listLoading,
    lineChart,
    barChart,
    doughnutChart,
    hasChartData,
    convertAmount,
    formatMoney,
    formatExpenseDate,
    listError,
    summaryError,
    ratesError,
    loadExpenses,
    loadRates,
    loadSummary,
    loadPreviousSummary,
    reloadListAndSummary,
  } = summaryHook;

  useScrollListFingerprint(() => {
    const params = expenseQueryParams();
    return `${activeTab.value}:${sortParam.value}:${expensePage.value}:${expenseTotal.value}:${JSON.stringify(params)}`;
  });

  async function reloadAfterMutation(): Promise<void> {
    await Promise.all([loadExpenses(), loadSummary(), loadPreviousSummary(), loadCategories()]);
  }

  async function reloadFiltersFromFirstPage(): Promise<void> {
    expensePage.value = 1;
    await reloadListAndSummary();
  }

  async function reloadProductFilterFromFirstPage(): Promise<void> {
    expensePage.value = 1;
    await loadExpenses();
  }

  function focusQuickAdd(): void {
    quickAddRef.value?.focusEntry();
  }

  function openSmartText(): void {
    smartTextOpen.value = true;
    switchTab("transactions");
    void nextTick(() => {
      quickAddRef.value?.focusSmartText();
    });
  }

  const filters = useExpenseFilters(
    displayCurrency as typeof displayCurrency & { value: CurrencyCode },
    reloadFiltersFromFirstPage,
    reloadProductFilterFromFirstPage,
  );
  filtersRef.value = filters;

  const {
    monthPreset,
    dateFilterMode,
    selectedMonth,
    dateFrom,
    dateTo,
    productFilter,
    categoryFilter,
    monthLabel,
    hasActiveFilters,
    rangeError,
    applyMonthPreset,
    clearFilters,
    queryParams,
  } = filters;

  const quickAddCurrency = computed(() => displayCurrency.value as CurrencyCode);

  const quickAdd = ref({
    price: "",
    category: lastCategory.value,
    product: "",
  });

  const form = ref({
    tool_name: "",
    amount: "",
    currency: EXPENSE_DEFAULT_CURRENCY as CurrencyCode,
    expense_date: isoDateLocal(),
    category: "",
    notes: "",
  });

  const { toast } = useNotify();

  const formTitle = computed(() => (editingId.value ? "edit expense" : "new expense"));
  const hasPreviousExpensePage = computed(() => expensePage.value > 1);
  const hasNextExpensePage = computed(() => expensePage.value < expensePages.value);
  const transactionFilterLabel = computed(() => {
    const count = [productFilter.value.trim(), categoryFilter.value].filter(Boolean).length;
    if (count === 0) return "filters";
    return `filters (${count})`;
  });

  const productSuggestions = computed(
    () => summary.value?.by_tool.map((item) => item.tool_name) ?? [],
  );

  function resolvedCategory(name: string): string {
    if (categoryOptions.value.includes(name)) return name;
    return defaultCategoryName.value;
  }

  function defaultCurrency(): CurrencyCode {
    const value = displayCurrency.value;
    return EXPENSE_CURRENCIES.includes(value as CurrencyCode)
      ? (value as CurrencyCode)
      : EXPENSE_DEFAULT_CURRENCY;
  }

  function resetForm(): void {
    form.value = {
      tool_name: "",
      amount: "",
      currency: defaultCurrency(),
      expense_date: isoDateLocal(),
      category: resolvedCategory(lastCategory.value),
      notes: "",
    };
    editingId.value = null;
  }

  function resetQuickAdd(): void {
    quickAdd.value = {
      price: "",
      category: resolvedCategory(lastCategory.value),
      product: "",
    };
  }

  async function postExpense(payload: {
    tool_name: string;
    amount: string;
    currency: CurrencyCode;
    expense_date: string;
    category: string | null;
    notes: string | null;
  }): Promise<void> {
    if (editingId.value) {
      await api.put(`/tools/expenses/${editingId.value}`, payload);
      toast("Expense updated", "success");
    } else {
      await api.post("/tools/expenses", payload);
      toast("Expense created", "success");
    }
    void saveDisplayCurrency(payload.currency);
    if (payload.category) {
      setLastCategory(payload.category);
    }
  }

  async function saveExpense(): Promise<void> {
    if (!form.value.tool_name.trim()) {
      toast("Product is required", "error");
      return;
    }
    if (!form.value.amount || !form.value.expense_date) {
      toast("Price and date are required", "error");
      return;
    }
    const amount = parseFloat(form.value.amount);
    if (Number.isNaN(amount) || amount <= 0) {
      toast("Price must be greater than zero", "error");
      return;
    }

    const payload = {
      tool_name: form.value.tool_name.trim(),
      amount: amount.toFixed(2),
      currency: form.value.currency,
      expense_date: form.value.expense_date,
      category: form.value.category.trim() || null,
      notes: form.value.notes.trim() || null,
    };

    const ok = await runSaveExpense(
      async () => {
        await postExpense(payload);
        return true;
      },
      { errorMessage: "Failed to save expense" },
    );
    if (!ok) return;
    showForm.value = false;
    resetForm();
    await reloadAfterMutation();
  }

  async function quickSaveExpense(): Promise<void> {
    const product = quickAdd.value.product.trim();
    if (!product) {
      toast("Enter a product name", "error");
      return;
    }

    const amount = parseFloat(quickAdd.value.price);
    if (Number.isNaN(amount) || amount <= 0) {
      toast("Enter a valid price", "error");
      return;
    }

    const category = resolvedCategory(quickAdd.value.category);
    const ok = await runSaveExpense(
      async () => {
        await postExpense({
          tool_name: product,
          amount: amount.toFixed(2),
          currency: defaultCurrency(),
          expense_date: isoDateLocal(),
          category,
          notes: null,
        });
        return true;
      },
      { errorMessage: "Failed to save expense" },
    );
    if (!ok) return;
    resetQuickAdd();
    await reloadAfterMutation();
    focusQuickAdd();
  }

  async function saveSmartExpense(payload: {
    tool_name: string;
    amount: string;
    currency: CurrencyCode;
    expense_date: string;
    category: string | null;
  }): Promise<void> {
    const ok = await runSaveExpense(
      async () => {
        await postExpense({
          ...payload,
          category: payload.category ? resolvedCategory(payload.category) : resolvedCategory(""),
          notes: null,
        });
        return true;
      },
      { errorMessage: "Failed to save expense" },
    );
    if (!ok) return;
    quickAddRef.value?.clearSmartText();
    await reloadAfterMutation();
    focusQuickAdd();
  }

  function handleDatePreset(preset: MonthPreset): void {
    applyMonthPreset(preset);
  }

  function clearTransactionFilters(): void {
    productFilter.value = "";
    categoryFilter.value = null;
  }

  function goToExpensePage(page: number): void {
    if (page < 1 || (expensePages.value > 0 && page > expensePages.value)) return;
    expensePage.value = page;
    void loadExpenses();
  }

  function handleExpenseSort(key: ExpenseSortKey): void {
    toggleSort(key);
    expensePage.value = 1;
    void loadExpenses();
  }

  function openEdit(expense: Expense): void {
    editingId.value = expense.id;
    form.value = {
      tool_name: expense.tool_name,
      amount: expense.amount,
      currency: expense.currency as CurrencyCode,
      expense_date: expense.expense_date,
      category: expense.category ?? "",
      notes: expense.notes ?? "",
    };
    showForm.value = true;
  }

  function openCreate(): void {
    resetForm();
    showForm.value = true;
  }

  async function duplicateExpense(expense: Expense): Promise<void> {
    quickAdd.value = {
      product: expense.tool_name,
      price: expense.amount,
      category: resolvedCategory(expense.category ?? lastCategory.value),
    };
    switchTab("transactions");
    toast("Ready to add again — adjust if needed", "success");
    await nextTick();
    focusQuickAdd();
  }

  async function exportCsv(): Promise<void> {
    await runExport(
      async () => {
        const { data } = await api.get<Blob>("/tools/expenses/export", {
          params: queryParams(),
          responseType: "blob",
        });
        const slug = monthLabel.value.replace(/\s+/g, "-").toLowerCase() || "export";
        const url = URL.createObjectURL(data);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = `expenses-${slug}.csv`;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        URL.revokeObjectURL(url);
      },
      { successMessage: "CSV exported", errorMessage: "Failed to export CSV" },
    );
  }

  function requestDeleteExpense(id: number): void {
    deleteTargetId.value = id;
  }

  async function confirmDeleteExpense(): Promise<void> {
    if (deleteTargetId.value === null) return;

    const id = deleteTargetId.value;
    const ok = await runDeleteExpense(
      async () => {
        await api.delete(`/tools/expenses/${id}`);
        return true;
      },
      { successMessage: "Expense deleted", errorMessage: "Failed to delete expense" },
    );
    if (!ok) return;
    deleteTargetId.value = null;
    await reloadAfterMutation();
  }

  watch(displayCurrency, (currency) => {
    void saveDisplayCurrency(currency);
    void Promise.all([loadSummary(), loadPreviousSummary()]);
  });

  watch(defaultCategoryName, (name) => {
    if (!categoryOptions.value.includes(quickAdd.value.category)) {
      quickAdd.value.category = name;
    }
  });

  watch(
    () => quickAdd.value.category,
    (category) => {
      if (categoryOptions.value.includes(category)) {
        setLastCategory(category);
      }
    },
  );

  /** Transaction-side mount: month preset, last category, list/summary/rates. */
  function bootstrapOnMount(): void {
    applyMonthPreset("this_month");
    quickAdd.value.category = resolvedCategory(lastCategory.value);
  }

  return {
    summaryHook,
    savingExpense,
    exporting,
    deletingExpense,
    smartTextOpen,
    filtersOpen,
    showForm,
    deleteTargetId,
    expensePage,
    expenses,
    expensePages,
    expenseTotal,
    summary,
    periodChange,
    exchangeRates,
    listLoading,
    lineChart,
    barChart,
    doughnutChart,
    hasChartData,
    convertAmount,
    formatMoney,
    formatExpenseDate,
    listError,
    summaryError,
    ratesError,
    loadExpenses,
    loadSummary,
    loadRates,
    loadPreviousSummary,
    reloadListAndSummary,
    reloadAfterMutation,
    monthPreset,
    dateFilterMode,
    selectedMonth,
    dateFrom,
    dateTo,
    productFilter,
    categoryFilter,
    monthLabel,
    hasActiveFilters,
    rangeError,
    clearFilters,
    applyMonthPreset,
    quickAddCurrency,
    quickAdd,
    form,
    formTitle,
    hasPreviousExpensePage,
    hasNextExpensePage,
    transactionFilterLabel,
    productSuggestions,
    sortIndicator,
    sortAriaSort,
    handleDatePreset,
    clearTransactionFilters,
    goToExpensePage,
    handleExpenseSort,
    openEdit,
    openCreate,
    openSmartText,
    duplicateExpense,
    exportCsv,
    requestDeleteExpense,
    confirmDeleteExpense,
    saveExpense,
    quickSaveExpense,
    saveSmartExpense,
    bootstrapOnMount,
  };
}
