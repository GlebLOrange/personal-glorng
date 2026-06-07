<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import ExpenseCategoryChips from "@/components/expenses/ExpenseCategoryChips.vue";
import ExpenseCategorySettings from "@/components/expenses/ExpenseCategorySettings.vue";
import ExpenseConfirmDialog from "@/components/expenses/ExpenseConfirmDialog.vue";
import ExpenseCurrencyConverter from "@/components/expenses/ExpenseCurrencyConverter.vue";
import ExpenseDateFilters from "@/components/expenses/ExpenseDateFilters.vue";
import ExpenseFormModal from "@/components/expenses/ExpenseFormModal.vue";
import ExpenseInsights from "@/components/expenses/ExpenseInsights.vue";
import ExpenseList from "@/components/expenses/ExpenseList.vue";
import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";
import ExpenseSummaryCard from "@/components/expenses/ExpenseSummaryCard.vue";
import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
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
import { useExpenseSort } from "@/composables/useExpenseSort";
import { useExpenseSummary } from "@/composables/useExpenseSummary";
import { api } from "@/composables/useApi";
import { useLocalStorageString } from "@/composables/useLocalStorage";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import { isoDateLocal } from "@/utils/dates";
import type { ToolExpense } from "@/types";

type ExpenseTab = "transactions" | "insights" | "converter" | "settings";

const EXPENSE_TABS: ExpenseTab[] = ["transactions", "insights", "converter", "settings"];
const expenseTabItems = EXPENSE_TABS.map((tab) => ({ id: tab, label: tab }));

const route = useRoute();
const router = useRouter();
const activeTab = ref<ExpenseTab>("transactions");
const loading = ref(false);
const showForm = ref(false);
const editingId = ref<number | null>(null);
const deleteTargetId = ref<number | null>(null);
const deleteCategoryTarget = ref<{ id: number; name: string } | null>(null);

const { displayCurrency, loadPreferences, saveDisplayCurrency } = useUserPreferences();

const { value: lastCategory, set: setLastCategory } = useLocalStorageString(
  EXPENSE_LAST_CATEGORY_STORAGE_KEY,
  DEFAULT_EXPENSE_CATEGORY,
);

// Assigned once below after summary/category hooks are wired.
// eslint-disable-next-line prefer-const
let filters!: ReturnType<typeof useExpenseFilters>;

const summaryHook = useExpenseSummary(
  () => filters.queryParams(),
  () => filters.summaryParams(),
  () => filters.previousSummaryParams(),
);

const {
  expenses,
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
  loadExpenses,
  loadRates,
  loadSummary,
  loadPreviousSummary,
  reloadListAndSummary,
} = summaryHook;

const { sortedExpenses, toggleSort, sortIndicator } = useExpenseSort(
  () => expenses.value,
  () => displayCurrency.value as CurrencyCode,
  convertAmount,
);

const quickAddRef = ref<InstanceType<typeof ExpenseQuickAdd> | null>(null);

async function reloadAfterMutation(): Promise<void> {
  await Promise.all([loadExpenses(), loadSummary(), loadPreviousSummary(), loadCategories()]);
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

filters = useExpenseFilters(
  displayCurrency as typeof displayCurrency & { value: CurrencyCode },
  reloadListAndSummary,
  loadExpenses,
);

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
  const count = expenses.value.length;
  return `${count} expense${count === 1 ? "" : "s"}`;
});

const productSuggestions = computed(() => summary.value?.by_tool.map((item) => item.tool_name) ?? []);

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
    console.error(err);
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
      console.error(err);
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
    console.error(err);
    toast(getApiErrorMessage(err, "Failed to save expense"), "error");
  } finally {
    loading.value = false;
  }
}

function handleDatePreset(preset: MonthPreset): void {
  applyMonthPreset(preset);
}

function openEdit(expense: ToolExpense): void {
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

async function duplicateExpense(expense: ToolExpense): Promise<void> {
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
    anchor.click();
    URL.revokeObjectURL(url);
    toast("CSV exported", "success");
  } catch (err) {
    console.error(err);
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
    console.error(err);
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
  return typeof value === "string" && EXPENSE_TABS.includes(value as ExpenseTab)
    ? (value as ExpenseTab)
    : null;
}

function switchTab(tab: string): void {
  if (!EXPENSE_TABS.includes(tab as ExpenseTab)) return;
  activeTab.value = tab as ExpenseTab;
  void router.replace({ query: { ...route.query, tab } });
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
  void Promise.all([
    loadPreferences(),
    loadRates(),
    reloadListAndSummary(),
    loadCategories(),
  ]);
});
</script>

<template>
  <AdminPageLayout title="monthly expenses" max-width="xl">
    <div class="flex flex-col gap-4 mb-6">
      <ExpenseDateFilters
        v-model:month-preset="monthPreset"
        v-model:date-filter-mode="dateFilterMode"
        v-model:selected-month="selectedMonth"
        v-model:date-from="dateFrom"
        v-model:date-to="dateTo"
        :has-active-filters="hasActiveFilters"
        @apply-preset="handleDatePreset"
        @clear-filters="clearFilters"
      />

      <ExpenseSummaryCard
        :summary="summary"
        :month-label="monthLabel"
        :expense-categories="expenseCategories"
        :period-change="periodChange"
        :format-money="formatMoney"
      />
    </div>

    <AdminTabBar :model-value="activeTab" :tabs="expenseTabItems" @update:model-value="switchTab" />

    <div v-if="activeTab === 'transactions'" class="flex flex-col gap-6">
      <ExpenseQuickAdd
        ref="quickAddRef"
        v-model:smart-text="smartText"
        v-model:category="quickAdd.category"
        v-model:product="quickAdd.product"
        v-model:price="quickAdd.price"
        :loading="loading"
        :parsing="parsing"
        :parsed="parsed"
        :category-options="categoryOptions"
        :product-suggestions="productSuggestions"
        :currency-label="quickAddCurrency"
        @submit="quickSaveExpense"
      />

      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1">
          <BaseInput v-model="productFilter" placeholder="Filter by product..." />
        </div>
        <div class="flex gap-2 items-end">
          <BaseButton variant="ghost" :disabled="loading" @click="exportCsv">Export CSV</BaseButton>
          <BaseButton variant="primary" @click="openCreate">+ Add</BaseButton>
        </div>
      </div>

      <ExpenseCategoryChips v-model:category-filter="categoryFilter" :category-options="categoryOptions" />

      <p class="text-xs text-surface-mid -mt-3">{{ expenseCountLabel }}</p>

      <ExpenseList
        :expenses="sortedExpenses"
        :loading="listLoading"
        :sort-indicator="sortIndicator"
        :month-label="monthLabel"
        :display-currency="displayCurrency as CurrencyCode"
        :exchange-rates="exchangeRates"
        :format-money="formatMoney"
        :format-expense-date="formatExpenseDate"
        :convert-amount="convertAmount"
        @edit="openEdit"
        @delete="requestDeleteExpense"
        @duplicate="duplicateExpense"
        @sort="toggleSort"
      />
    </div>

    <ExpenseInsights
      v-else-if="activeTab === 'insights'"
      :has-chart-data="hasChartData"
      :line-chart="lineChart"
      :bar-chart="barChart"
      :doughnut-chart="doughnutChart"
    />

    <ExpenseCurrencyConverter
      v-else-if="activeTab === 'converter'"
      :exchange-rates="exchangeRates"
    />

    <ExpenseCategorySettings
      v-else-if="activeTab === 'settings'"
      v-model:display-currency="displayCurrency"
      v-model:new-category-name="newCategoryName"
      v-model:editing-category-name="editingCategoryName"
      v-model:editing-category-budget="editingCategoryBudget"
      :expense-categories="expenseCategories"
      :editing-category-id="editingCategoryId"
      :exchange-rates="exchangeRates"
      @add-category="addCategory"
      @start-edit-category="startEditCategory"
      @cancel-edit-category="cancelEditCategory"
      @save-category-rename="saveCategoryRename"
      @remove-category="requestDeleteCategory"
    />

    <ExpenseFormModal
      v-model:category="form.category"
      v-model:tool-name="form.tool_name"
      v-model:amount="form.amount"
      v-model:currency="form.currency"
      v-model:expense-date="form.expense_date"
      v-model:notes="form.notes"
      :open="showForm"
      :loading="loading"
      :title="formTitle"
      :category-options="categoryOptions"
      @submit="saveExpense"
      @close="showForm = false"
    />

    <ExpenseConfirmDialog
      :open="deleteTargetId !== null"
      title="Delete expense"
      message="This expense will be permanently removed."
      confirm-label="Delete"
      :loading="loading"
      @confirm="confirmDeleteExpense"
      @cancel="deleteTargetId = null"
    />

    <ExpenseConfirmDialog
      :open="deleteCategoryTarget !== null"
      title="Delete category"
      :message="deleteCategoryTarget ? `Delete category '${deleteCategoryTarget.name}'?` : ''"
      confirm-label="Delete"
      :loading="loading"
      @confirm="confirmDeleteCategory"
      @cancel="deleteCategoryTarget = null"
    />
  </AdminPageLayout>
</template>
