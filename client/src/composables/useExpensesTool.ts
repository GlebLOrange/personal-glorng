import { computed, nextTick, onMounted, ref, shallowRef, watch, type Ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";
import { DEFAULT_EXPENSE_CATEGORY } from "@/constants/expenseCategories";
import { useCategoryManager } from "@/composables/useCategoryManager";
import {
  EXPENSE_CURRENCIES,
  EXPENSE_DEFAULT_CURRENCY,
  EXPENSE_LAST_CATEGORY_STORAGE_KEY,
  useExpenseFilters,
  type CurrencyCode,
  type MonthPreset,
} from "@/composables/useExpenseFilters";
import { useUserPreferences } from "@/composables/useUserPreferences";
import { useExpenseParse } from "@/composables/useExpenseParse";
import { useExpenseSort, type ExpenseSortKey } from "@/composables/useExpenseSort";
import { useExpenseSummary } from "@/composables/useExpenseSummary";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { api } from "@/composables/useApi";
import { useLocalStorageString } from "@/composables/useLocalStorage";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import { isoDateLocal } from "@/utils/dates";
import type { Expense } from "@/types";

export type ExpenseCalculatorTab = "convert" | "sum" | "budget" | "whatif";

export type ExpenseTab =
  | "transactions"
  | "insights"
  | ExpenseCalculatorTab
  | "settings";

const EXPENSE_PER_PAGE = 20;
const CALCULATOR_TABS: ExpenseCalculatorTab[] = ["convert", "sum", "budget", "whatif"];
const EXPENSE_TABS: ExpenseTab[] = [
  "transactions",
  "insights",
  ...CALCULATOR_TABS,
  "settings",
];

const TAB_LABELS: Record<ExpenseTab, string> = {
  transactions: "Transactions",
  insights: "Insights",
  convert: "Convert",
  sum: "Sum",
  budget: "Budget",
  whatif: "What-if",
  settings: "Settings",
};

export const expenseTabItems = EXPENSE_TABS.map((tab) => ({
  id: tab,
  label: TAB_LABELS[tab],
}));

export function isCalculatorTab(tab: string): tab is ExpenseCalculatorTab {
  return CALCULATOR_TABS.includes(tab as ExpenseCalculatorTab);
}

/** Orchestrates expense tool state: filters, list, charts, forms, and mutations. */
export function useExpensesTool(
  quickAddRef: Ref<InstanceType<typeof ExpenseQuickAdd> | null> = ref(null),
) {
  const route = useRoute();
  const router = useRouter();
  const activeTab = ref<ExpenseTab>("transactions");
  const loading = ref(false);
  const filtersOpen = ref(false);
  const showForm = ref(false);
  const editingId = ref<number | null>(null);
  const deleteTargetId = ref<number | null>(null);
  const deleteCategoryTarget = ref<{ id: number; name: string } | null>(null);
  const expensePage = ref(1);

  const { displayCurrency, loadPreferences, saveDisplayCurrency } = useUserPreferences();

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
      per_page: String(EXPENSE_PER_PAGE),
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

  const categoryManager = useCategoryManager(reloadAfterMutation);

  const {
    expenseCategories,
    newCategoryName,
    editingCategoryId,
    editingCategoryName,
    editingCategoryBudget,
    categoryOptions,
    defaultCategoryName,
    loadCategories,
    addCategory,
    startEditCategory,
    cancelEditCategory,
    saveCategoryRename,
    removeCategory: removeCategoryRaw,
  } = categoryManager;

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

  const smartText = ref("");
  const quickAddCurrency = computed(() => displayCurrency.value as CurrencyCode);
  const { parsed, parsing } = useExpenseParse(smartText, quickAddCurrency);

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
  const expenseCountLabel = computed(() => {
    const count = expenseTotal.value;
    const pageLabel =
      expensePages.value > 0 ? ` · page ${expensePage.value} of ${expensePages.value}` : "";
    return `${count} expense${count === 1 ? "" : "s"}${pageLabel}`;
  });
  const hasPreviousExpensePage = computed(() => expensePage.value > 1);
  const hasNextExpensePage = computed(() => expensePage.value < expensePages.value);
  const transactionFilterLabel = computed(() => {
    const count = [productFilter.value.trim(), categoryFilter.value].filter(Boolean).length;
    if (count === 0) return "Filters";
    return `Filters (${count})`;
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
    smartText.value = "";
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

    loading.value = true;
    const payload = {
      tool_name: form.value.tool_name.trim(),
      amount: amount.toFixed(2),
      currency: form.value.currency,
      expense_date: form.value.expense_date,
      category: form.value.category.trim() || null,
      notes: form.value.notes.trim() || null,
    };

    try {
      await postExpense(payload);
      showForm.value = false;
      resetForm();
      await reloadAfterMutation();
    } catch (err) {
      if (import.meta.env.DEV) console.error(err);
      toast(getApiErrorMessage(err, "Failed to save expense"), "error");
    } finally {
      loading.value = false;
    }
  }

  async function quickSaveExpense(): Promise<void> {
    if (smartText.value.trim()) {
      if (!parsed.value?.valid) {
        toast(parsed.value?.error ?? "Could not parse expense", "error");
        return;
      }

      loading.value = true;
      try {
        await postExpense({
          tool_name: parsed.value.tool_name ?? "",
          amount: String(parsed.value.amount),
          currency: (parsed.value.currency as CurrencyCode) ?? defaultCurrency(),
          expense_date: parsed.value.expense_date ?? isoDateLocal(),
          category: resolvedCategory(parsed.value.category ?? lastCategory.value),
          notes: null,
        });
        resetQuickAdd();
        await reloadAfterMutation();
        focusQuickAdd();
      } catch (err) {
        if (import.meta.env.DEV) console.error(err);
        toast(getApiErrorMessage(err, "Failed to save expense"), "error");
      } finally {
        loading.value = false;
      }
      return;
    }

    const product = quickAdd.value.product.trim();
    if (!product) {
      toast("Enter smart text or a product name", "error");
      return;
    }

    const amount = parseFloat(quickAdd.value.price);
    if (Number.isNaN(amount) || amount <= 0) {
      toast("Enter a valid price", "error");
      return;
    }

    loading.value = true;
    const category = resolvedCategory(quickAdd.value.category);
    try {
      await postExpense({
        tool_name: product,
        amount: amount.toFixed(2),
        currency: defaultCurrency(),
        expense_date: isoDateLocal(),
        category,
        notes: null,
      });
      resetQuickAdd();
      await reloadAfterMutation();
      focusQuickAdd();
    } catch (err) {
      if (import.meta.env.DEV) console.error(err);
      toast(getApiErrorMessage(err, "Failed to save expense"), "error");
    } finally {
      loading.value = false;
    }
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
    smartText.value = "";
    quickAdd.value = {
      product: expense.tool_name,
      price: expense.amount,
      category: resolvedCategory(expense.category ?? lastCategory.value),
    };
    activeTab.value = "transactions";
    toast("Ready to add again — adjust if needed", "success");
    await nextTick();
    focusQuickAdd();
  }

  async function exportCsv(): Promise<void> {
    loading.value = true;
    try {
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
      toast("CSV exported", "success");
    } catch (err) {
      if (import.meta.env.DEV) console.error(err);
      toast(getApiErrorMessage(err, "Failed to export CSV"), "error");
    } finally {
      loading.value = false;
    }
  }

  function requestDeleteExpense(id: number): void {
    deleteTargetId.value = id;
  }

  async function confirmDeleteExpense(): Promise<void> {
    if (deleteTargetId.value === null) return;

    loading.value = true;
    try {
      await api.delete(`/tools/expenses/${deleteTargetId.value}`);
      toast("Expense deleted", "success");
      deleteTargetId.value = null;
      await reloadAfterMutation();
    } catch (err) {
      if (import.meta.env.DEV) console.error(err);
      toast(getApiErrorMessage(err, "Failed to delete expense"), "error");
    } finally {
      loading.value = false;
    }
  }

  function requestDeleteCategory(category: { id: number; name: string }): void {
    deleteCategoryTarget.value = category;
  }

  async function confirmDeleteCategory(): Promise<void> {
    if (!deleteCategoryTarget.value) return;
    const category = expenseCategories.value.find((c) => c.id === deleteCategoryTarget.value!.id);
    if (!category) {
      deleteCategoryTarget.value = null;
      return;
    }

    loading.value = true;
    try {
      await removeCategoryRaw(category);
      deleteCategoryTarget.value = null;
    } finally {
      loading.value = false;
    }
  }

  function parseExpenseTab(value: unknown): ExpenseTab | null {
    if (typeof value !== "string") return null;
    if (value === "converter") return "convert";
    return EXPENSE_TABS.includes(value as ExpenseTab) ? (value as ExpenseTab) : null;
  }

  function switchTab(tab: string): void {
    if (!EXPENSE_TABS.includes(tab as ExpenseTab)) return;
    activeTab.value = tab as ExpenseTab;
    const { mode: _legacyMode, ...rest } = route.query;
    void router.replace({ query: { ...rest, tab } });
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

  onMounted(() => {
    const tab = parseExpenseTab(route.query.tab);
    if (tab) activeTab.value = tab;
    applyMonthPreset("this_month");
    quickAdd.value.category = resolvedCategory(lastCategory.value);
    void Promise.all([loadPreferences(), loadRates(), reloadListAndSummary(), loadCategories()]);
  });

  return {
    activeTab,
    expenseTabItems,
    loading,
    filtersOpen,
    showForm,
    deleteTargetId,
    deleteCategoryTarget,
    expensePage,
    displayCurrency,
    expenses,
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
    expenseCategories,
    newCategoryName,
    editingCategoryId,
    editingCategoryName,
    editingCategoryBudget,
    categoryOptions,
    addCategory,
    startEditCategory,
    cancelEditCategory,
    saveCategoryRename,
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
    smartText,
    quickAddCurrency,
    parsed,
    parsing,
    quickAdd,
    form,
    formTitle,
    expenseCountLabel,
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
    duplicateExpense,
    exportCsv,
    requestDeleteExpense,
    confirmDeleteExpense,
    requestDeleteCategory,
    confirmDeleteCategory,
    switchTab,
    saveExpense,
    quickSaveExpense,
  };
}
