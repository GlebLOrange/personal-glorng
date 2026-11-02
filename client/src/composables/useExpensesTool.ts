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

export type ExpenseTab = "today" | "activity" | "insights" | "categories" | "converter";

const EXPENSE_TABS: ExpenseTab[] = ["today", "activity", "insights", "categories", "converter"];

const TAB_LABELS: Record<ExpenseTab, string> = {
  today: "money",
  activity: "activity",
  insights: "insights",
  categories: "categories",
  converter: "converter",
};

/** Legacy ?tab= values → current tab ids. */
const TAB_ALIASES: Record<string, ExpenseTab> = {
  expenses: "today",
  transactions: "activity",
  breakdown: "insights",
  analytics: "insights",
  insights: "insights",
  "category-breakdown": "insights",
  settings: "categories",
  currency: "today",
  calculator: "converter",
};

const TAB_ICONS: Record<ExpenseTab, "calendar" | "queue" | "intakes" | "tag" | "sync"> = {
  today: "calendar",
  activity: "queue",
  insights: "intakes",
  categories: "tag",
  converter: "sync",
};

export const expenseTabItems = EXPENSE_TABS.map((id) => ({
  id,
  label: TAB_LABELS[id],
  icon: TAB_ICONS[id],
}));

function resolveExpenseTab(value: unknown): ExpenseTab | null {
  if (typeof value !== "string") return null;
  if (EXPENSE_TABS.includes(value as ExpenseTab)) return value as ExpenseTab;
  return TAB_ALIASES[value] ?? null;
}

/**
 * Thin orchestrator: route tab sync + compose transactions, insights slice, and category settings.
 * ExpensesTool.vue keeps importing from this module for a stable public API.
 */
export function useExpensesTool(quickAddRef: Ref<ExpenseQuickAddTarget | null> = ref(null)) {
  const route = useRoute();
  const router = useRouter();
  const activeTab = ref<ExpenseTab>("today");
  const converterMode = ref<ExpenseCalculatorMode>("convert");
  /** Keep converter mounted after first visit so amount/pair survive. */
  const converterMounted = ref(false);

  const { displayCurrency, loadPreferences, saveDisplayCurrency } = useUserPreferences();

  // Late-bound so category settings can trigger a full post-mutation reload once transactions exist.
  let reloadAfterMutation: () => Promise<void> = async () => {};

  const categorySettings = useExpenseCategorySettings(() => reloadAfterMutation());

  function syncTabFromRoute(): void {
    const raw = route.query.tab;

    if (route.hash === "#expenses-analytics") {
      activeTab.value = "insights";
      const { mode: _mode, panel: _panel, ...rest } = route.query;
      void router.replace({ query: { ...rest, tab: "insights" }, hash: "" });
      return;
    }

    // Legacy ?panel= overflow deep-links → real tabs.
    const panel = route.query.panel;
    if (typeof panel === "string") {
      const resolvedPanel =
        (EXPENSE_TABS.includes(panel as ExpenseTab) ? (panel as ExpenseTab) : null) ??
        TAB_ALIASES[panel] ??
        null;
      if (resolvedPanel) {
        const { panel: _panel, ...rest } = route.query;
        void router.replace({ query: { ...rest, tab: resolvedPanel } });
        return;
      }
    }

    // Calculator mode ids as ?tab= → converter tab + mode.
    if (typeof raw === "string" && isCalculatorMode(raw)) {
      const mode = normalizeCalculatorMode(raw);
      activeTab.value = "converter";
      converterMode.value = mode;
      converterMounted.value = true;
      void router.replace({ query: { ...route.query, tab: "converter", mode } });
      return;
    }

    const tab = resolveExpenseTab(raw);
    if (!tab) {
      if (raw == null) {
        activeTab.value = "today";
      }
      return;
    }
    activeTab.value = tab;
    if (tab === "converter") {
      converterMounted.value = true;
      if (typeof route.query.mode === "string") {
        converterMode.value = normalizeCalculatorMode(route.query.mode);
      }
    }

    // Canonicalize legacy aliases in the URL.
    if (typeof raw === "string" && raw !== tab) {
      const { mode: _mode, panel: _panel, ...rest } = route.query;
      const query =
        tab === "converter" ? { ...rest, tab, mode: converterMode.value } : { ...rest, tab };
      void router.replace({ query });
    }
  }

  function switchTab(tab: string): void {
    const resolved = resolveExpenseTab(tab);
    if (!resolved) return;
    activeTab.value = resolved;
    if (resolved === "converter") {
      converterMounted.value = true;
    }
    const { mode: _mode, panel: _panel, ...rest } = route.query;
    const query =
      resolved === "converter"
        ? { ...rest, tab: resolved, mode: converterMode.value }
        : { ...rest, tab: resolved };
    void router.replace({ query });
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

  watch(activeTab, (tab) => {
    if (tab === "today") {
      transactions.handleDatePreset("this_month");
    }
  });

  onMounted(() => {
    syncTabFromRoute();
    transactions.bootstrapOnMount();
    // List + summary + categories first; rates / previous-summary deferred inside bootstrap.
    void Promise.all([
      loadPreferences(),
      transactions.bootstrapListAndSummary(),
      categorySettings.loadCategories(),
    ]);
  });

  return {
    activeTab,
    expenseTabItems,
    converterMode,
    converterMounted,
    savingExpense: transactions.savingExpense,
    exporting: transactions.exporting,
    deletingExpense: transactions.deletingExpense,
    deletingCategory: categorySettings.deletingCategory,
    smartTextOpen: transactions.smartTextOpen,
    showForm: transactions.showForm,
    deleteTargetId: transactions.deleteTargetId,
    deleteCategoryTarget: categorySettings.deleteCategoryTarget,
    deleteCategoryReplacementId: categorySettings.deleteCategoryReplacementId,
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
    quickAddNameError: transactions.quickAddNameError,
    quickAddAmountError: transactions.quickAddAmountError,
    form: transactions.form,
    formTitle: transactions.formTitle,
    expenseTotal: transactions.expenseTotal,
    hasPreviousExpensePage: transactions.hasPreviousExpensePage,
    hasNextExpensePage: transactions.hasNextExpensePage,
    productSuggestions: transactions.productSuggestions,
    sortIndicator: transactions.sortIndicator,
    sortAriaSort: transactions.sortAriaSort,
    handleDatePreset: transactions.handleDatePreset,
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
    saveDisplayCurrency,
  };
}
