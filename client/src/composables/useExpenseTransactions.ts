import { computed, ref, shallowRef, watch, type ComputedRef, type Ref } from "vue";

import { LIST_PAGE_SIZE } from "@/constants/pagination";
import {
  useExpenseFilters,
  type CurrencyCode,
  type MonthPreset,
} from "@/composables/useExpenseFilters";
import {
  useExpenseFormMutations,
  type ExpenseQuickAddTarget,
} from "@/composables/useExpenseFormMutations";
import { useExpenseSort, type ExpenseSortKey } from "@/composables/useExpenseSort";
import { useExpenseSummary } from "@/composables/useExpenseSummary";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";

export type { ExpenseQuickAddTarget };

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

/** List, filters, sort, pagination, and export — form/CRUD via useExpenseFormMutations. */
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

  const { run: runExport, loading: exporting } = useApiAction();
  const expensePage = ref(1);

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
    bootstrapListAndSummary,
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

  const formMutations = useExpenseFormMutations({
    quickAddRef,
    switchTab,
    displayCurrency,
    saveDisplayCurrency,
    categoryOptions,
    defaultCategoryName,
    reloadAfterMutation,
  });

  const hasPreviousExpensePage = computed(() => expensePage.value > 1);
  const hasNextExpensePage = computed(() => expensePage.value < expensePages.value);

  const productSuggestions = computed(
    () => summary.value?.by_tool.map((item) => item.tool_name) ?? [],
  );

  function handleDatePreset(preset: MonthPreset): void {
    applyMonthPreset(preset);
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

  watch(displayCurrency, (currency) => {
    void saveDisplayCurrency(currency);
    void Promise.all([loadSummary(), loadPreviousSummary()]);
  });

  /** Transaction-side mount: month preset, last category, list/summary/rates. */
  function bootstrapOnMount(): void {
    applyMonthPreset("this_month");
    formMutations.bootstrapFormOnMount();
  }

  return {
    summaryHook,
    exporting,
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
    bootstrapListAndSummary,
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
    hasPreviousExpensePage,
    hasNextExpensePage,
    productSuggestions,
    sortIndicator,
    sortAriaSort,
    handleDatePreset,
    goToExpensePage,
    handleExpenseSort,
    exportCsv,
    bootstrapOnMount,
    savingExpense: formMutations.savingExpense,
    deletingExpense: formMutations.deletingExpense,
    smartTextOpen: formMutations.smartTextOpen,
    showForm: formMutations.showForm,
    deleteTargetId: formMutations.deleteTargetId,
    quickAddCurrency: formMutations.quickAddCurrency,
    quickAdd: formMutations.quickAdd,
    quickAddNameError: formMutations.quickAddNameError,
    quickAddAmountError: formMutations.quickAddAmountError,
    form: formMutations.form,
    formTitle: formMutations.formTitle,
    openEdit: formMutations.openEdit,
    openCreate: formMutations.openCreate,
    openSmartText: formMutations.openSmartText,
    duplicateExpense: formMutations.duplicateExpense,
    requestDeleteExpense: formMutations.requestDeleteExpense,
    confirmDeleteExpense: formMutations.confirmDeleteExpense,
    saveExpense: formMutations.saveExpense,
    quickSaveExpense: formMutations.quickSaveExpense,
    saveSmartExpense: formMutations.saveSmartExpense,
  };
}
