import { onMounted, ref, watch, type Ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import {
  isCalculatorMode,
  normalizeCalculatorMode,
  type ExpenseCalculatorMode,
} from "@/composables/useExpenseCalculator";
import { useExpenseCategorySettings } from "@/composables/useExpenseCategorySettings";
import { useExpenseInsightsState } from "@/composables/useExpenseInsightsState";
import {
  useExpenseTransactions,
  type ExpenseQuickAddTarget,
} from "@/composables/useExpenseTransactions";
import { useUserPreferences } from "@/composables/useUserPreferences";

export type { ExpenseCalculatorMode, ExpenseQuickAddTarget };
export { isCalculatorMode, normalizeCalculatorMode };

export type ExpenseTab = "transactions" | "insights" | "calculator" | "settings";

const EXPENSE_TABS: ExpenseTab[] = ["transactions", "insights", "calculator", "settings"];

const TAB_LABELS: Record<ExpenseTab, string> = {
  transactions: "transactions",
  insights: "insights",
  calculator: "calculator",
  settings: "settings",
};

export const expenseTabItems = EXPENSE_TABS.map((tab) => ({
  id: tab,
  label: TAB_LABELS[tab],
}));

/** True when the top-level expenses tab is the nested calculator panel. */
export function isCalculatorTab(tab: string): boolean {
  return tab === "calculator";
}

/**
 * Thin orchestrator: route tab sync + compose transactions, insights slice, and category settings.
 * ExpensesTool.vue keeps importing from this module for a stable public API.
 */
export function useExpensesTool(quickAddRef: Ref<ExpenseQuickAddTarget | null> = ref(null)) {
  const route = useRoute();
  const router = useRouter();
  const activeTab = ref<ExpenseTab>("transactions");

  const { displayCurrency, loadPreferences, saveDisplayCurrency } = useUserPreferences();

  // Late-bound so category settings can trigger a full post-mutation reload once transactions exist.
  let reloadAfterMutation: () => Promise<void> = async () => {};

  const categorySettings = useExpenseCategorySettings(() => reloadAfterMutation());

  function parseExpenseTab(value: unknown): ExpenseTab | null {
    if (typeof value !== "string") return null;
    return EXPENSE_TABS.includes(value as ExpenseTab) ? (value as ExpenseTab) : null;
  }

  function syncTabFromRoute(): void {
    const raw = route.query.tab;
    if (typeof raw === "string" && (isCalculatorMode(raw) || raw === "converter")) {
      const mode = normalizeCalculatorMode(raw);
      activeTab.value = "calculator";
      void router.replace({ query: { ...route.query, tab: "calculator", mode } });
      return;
    }
    const tab = parseExpenseTab(raw);
    if (tab) activeTab.value = tab;
  }

  function switchTab(tab: string): void {
    if (!EXPENSE_TABS.includes(tab as ExpenseTab)) return;
    activeTab.value = tab as ExpenseTab;
    if (tab === "calculator") {
      const existing =
        typeof route.query.mode === "string"
          ? normalizeCalculatorMode(route.query.mode)
          : "convert";
      void router.replace({ query: { ...route.query, tab: "calculator", mode: existing } });
      return;
    }
    const { mode: _mode, ...rest } = route.query;
    void router.replace({ query: { ...rest, tab } });
  }

  const transactions = useExpenseTransactions({
    quickAddRef,
    activeTab,
    switchTab,
    displayCurrency,
    saveDisplayCurrency,
    categoryOptions: categorySettings.categoryOptions,
    defaultCategoryName: categorySettings.defaultCategoryName,
    loadCategories: categorySettings.loadCategories,
  });

  reloadAfterMutation = transactions.reloadAfterMutation;

  const insights = useExpenseInsightsState(transactions.summaryHook);

  watch(
    () => route.query.tab,
    () => {
      syncTabFromRoute();
    },
  );

  onMounted(() => {
    syncTabFromRoute();
    transactions.bootstrapOnMount();
    void Promise.all([
      loadPreferences(),
      transactions.loadRates(),
      transactions.reloadListAndSummary(),
      categorySettings.loadCategories(),
    ]);
  });

  return {
    activeTab,
    expenseTabItems,
    savingExpense: transactions.savingExpense,
    exporting: transactions.exporting,
    deletingExpense: transactions.deletingExpense,
    deletingCategory: categorySettings.deletingCategory,
    smartTextOpen: transactions.smartTextOpen,
    filtersOpen: transactions.filtersOpen,
    showForm: transactions.showForm,
    deleteTargetId: transactions.deleteTargetId,
    deleteCategoryTarget: categorySettings.deleteCategoryTarget,
    expensePage: transactions.expensePage,
    displayCurrency,
    expenses: transactions.expenses,
    expensePages: transactions.expensePages,
    summary: insights.summary,
    periodChange: insights.periodChange,
    exchangeRates: insights.exchangeRates,
    listLoading: transactions.listLoading,
    lineChart: insights.lineChart,
    barChart: insights.barChart,
    doughnutChart: insights.doughnutChart,
    hasChartData: insights.hasChartData,
    convertAmount: insights.convertAmount,
    formatMoney: insights.formatMoney,
    formatExpenseDate: transactions.formatExpenseDate,
    listError: transactions.listError,
    summaryError: insights.summaryError,
    ratesError: insights.ratesError,
    loadSummary: insights.loadSummary,
    loadRates: insights.loadRates,
    expenseCategories: categorySettings.expenseCategories,
    newCategoryName: categorySettings.newCategoryName,
    editingCategoryId: categorySettings.editingCategoryId,
    editingCategoryName: categorySettings.editingCategoryName,
    editingCategoryBudget: categorySettings.editingCategoryBudget,
    categoryOptions: categorySettings.categoryOptions,
    addCategory: categorySettings.addCategory,
    startEditCategory: categorySettings.startEditCategory,
    cancelEditCategory: categorySettings.cancelEditCategory,
    saveCategoryRename: categorySettings.saveCategoryRename,
    monthPreset: transactions.monthPreset,
    dateFilterMode: transactions.dateFilterMode,
    selectedMonth: transactions.selectedMonth,
    dateFrom: transactions.dateFrom,
    dateTo: transactions.dateTo,
    productFilter: transactions.productFilter,
    categoryFilter: transactions.categoryFilter,
    monthLabel: transactions.monthLabel,
    hasActiveFilters: transactions.hasActiveFilters,
    rangeError: transactions.rangeError,
    clearFilters: transactions.clearFilters,
    quickAddCurrency: transactions.quickAddCurrency,
    quickAdd: transactions.quickAdd,
    form: transactions.form,
    formTitle: transactions.formTitle,
    expenseTotal: transactions.expenseTotal,
    hasPreviousExpensePage: transactions.hasPreviousExpensePage,
    hasNextExpensePage: transactions.hasNextExpensePage,
    transactionFilterLabel: transactions.transactionFilterLabel,
    productSuggestions: transactions.productSuggestions,
    sortIndicator: transactions.sortIndicator,
    sortAriaSort: transactions.sortAriaSort,
    handleDatePreset: transactions.handleDatePreset,
    clearTransactionFilters: transactions.clearTransactionFilters,
    goToExpensePage: transactions.goToExpensePage,
    handleExpenseSort: transactions.handleExpenseSort,
    openEdit: transactions.openEdit,
    openCreate: transactions.openCreate,
    openSmartText: transactions.openSmartText,
    duplicateExpense: transactions.duplicateExpense,
    exportCsv: transactions.exportCsv,
    requestDeleteExpense: transactions.requestDeleteExpense,
    confirmDeleteExpense: transactions.confirmDeleteExpense,
    requestDeleteCategory: categorySettings.requestDeleteCategory,
    confirmDeleteCategory: categorySettings.confirmDeleteCategory,
    switchTab,
    saveExpense: transactions.saveExpense,
    quickSaveExpense: transactions.quickSaveExpense,
    saveSmartExpense: transactions.saveSmartExpense,
  };
}
