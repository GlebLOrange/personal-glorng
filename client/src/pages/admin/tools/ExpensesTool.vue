<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import ExpenseCategorySettings from "@/components/expenses/ExpenseCategorySettings.vue";
import ExpenseConfirmDialog from "@/components/expenses/ExpenseConfirmDialog.vue";
import ExpenseFormModal from "@/components/expenses/ExpenseFormModal.vue";
import ExpenseInsights from "@/components/expenses/ExpenseInsights.vue";
import ExpenseList from "@/components/expenses/ExpenseList.vue";
import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";
import ExpenseSummaryCard from "@/components/expenses/ExpenseSummaryCard.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { useCategoryManager } from "@/composables/useCategoryManager";
import {
  EXPENSE_CURRENCIES,
  EXPENSE_CURRENCY_STORAGE_KEY,
  EXPENSE_LAST_CATEGORY_STORAGE_KEY,
  useExpenseFilters,
  type CurrencyCode,
  type MonthPreset,
} from "@/composables/useExpenseFilters";
import { useExpenseSummary } from "@/composables/useExpenseSummary";
import { api } from "@/composables/useApi";
import { useLocalStorageString } from "@/composables/useLocalStorage";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import type { ToolExpense } from "@/types";

type ExpenseTab = "transactions" | "insights" | "settings";

const activeTab = ref<ExpenseTab>("transactions");
const loading = ref(false);
const showForm = ref(false);
const editingId = ref<number | null>(null);
const deleteTargetId = ref<number | null>(null);
const deleteCategoryTarget = ref<{ id: number; name: string } | null>(null);

const { value: displayCurrency, set: setDisplayCurrency } = useLocalStorageString(
  EXPENSE_CURRENCY_STORAGE_KEY,
  "PLN",
);

const { value: lastCategory, set: setLastCategory } = useLocalStorageString(
  EXPENSE_LAST_CATEGORY_STORAGE_KEY,
  "Groceries",
);

// Assigned once below after summary/category hooks are wired.
// eslint-disable-next-line prefer-const
let filters!: ReturnType<typeof useExpenseFilters>;

const summaryHook = useExpenseSummary(
  () => filters.queryParams(),
  () => filters.summaryParams(),
);

const {
  expenses,
  summary,
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
  reloadListAndSummary,
} = summaryHook;

async function reloadAfterMutation(): Promise<void> {
  await Promise.all([loadExpenses(), loadSummary(), loadCategories()]);
}

const categoryManager = useCategoryManager(reloadAfterMutation);

const {
  expenseCategories,
  newCategoryName,
  editingCategoryId,
  editingCategoryName,
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

const { monthPreset, selectedMonth, productFilter, categoryFilter, monthLabel, applyMonthPreset } =
  filters;

const quickAdd = ref({
  price: "",
  category: lastCategory.value,
  product: "",
});

const form = ref({
  tool_name: "",
  amount: "",
  currency: "PLN" as CurrencyCode,
  expense_date: new Date().toISOString().slice(0, 10),
  category: "",
  notes: "",
});

const { toast } = useNotify();

const formTitle = computed(() => (editingId.value ? "edit expense" : "new expense"));
const quickAddCurrency = computed(() => displayCurrency.value as CurrencyCode);
const expenseCountLabel = computed(() => {
  const count = expenses.value.length;
  return `${count} expense${count === 1 ? "" : "s"}`;
});

function resolvedCategory(name: string): string {
  if (categoryOptions.value.includes(name)) return name;
  return defaultCategoryName.value;
}

function defaultCurrency(): CurrencyCode {
  const value = displayCurrency.value;
  return EXPENSE_CURRENCIES.includes(value as CurrencyCode) ? (value as CurrencyCode) : "PLN";
}

function resetForm(): void {
  form.value = {
    tool_name: "",
    amount: "",
    currency: defaultCurrency(),
    expense_date: new Date().toISOString().slice(0, 10),
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
  setDisplayCurrency(payload.currency);
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
  const product = quickAdd.value.product.trim();
  if (!product) {
    toast("Product is required", "error");
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
      expense_date: new Date().toISOString().slice(0, 10),
      category,
      notes: null,
    });
    resetQuickAdd();
    await reloadAfterMutation();
  } catch (err) {
    console.error(err);
    toast(getApiErrorMessage(err, "Failed to save expense"), "error");
  } finally {
    loading.value = false;
  }
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

function switchTab(tab: ExpenseTab): void {
  activeTab.value = tab;
}

watch(displayCurrency, () => {
  void loadSummary();
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
  applyMonthPreset("this_month");
  quickAdd.value.category = resolvedCategory(lastCategory.value);
  void Promise.all([loadRates(), reloadListAndSummary(), loadCategories()]);
});
</script>

<template>
  <AdminPageLayout title="monthly expenses" max-width="xl">
    <div class="flex flex-col gap-4 mb-6">
      <div class="flex flex-wrap gap-2 items-center">
        <BaseButton
          v-for="preset in ['this_month', 'last_month', 'custom'] as MonthPreset[]"
          :key="preset"
          :variant="monthPreset === preset ? 'primary' : 'ghost'"
          size="sm"
          @click="applyMonthPreset(preset)"
        >
          {{
            preset === "this_month"
              ? "This month"
              : preset === "last_month"
                ? "Last month"
                : "Custom"
          }}
        </BaseButton>
        <input
          v-model="selectedMonth"
          type="month"
          class="bg-surface-dark border border-surface-border rounded-lg px-3 py-1.5 text-surface-light font-mono text-sm focus:outline-none focus:border-accent-blue h-[34px]"
          @change="monthPreset = 'custom'"
        />
      </div>

      <ExpenseSummaryCard
        :summary="summary"
        :month-label="monthLabel"
        :format-money="formatMoney"
      />
    </div>

    <div class="flex gap-2 mb-6 border-b border-surface-border pb-2">
      <button
        v-for="tab in ['transactions', 'insights', 'settings'] as ExpenseTab[]"
        :key="tab"
        :class="[
          'px-3 py-1.5 text-xs font-mono rounded-lg transition-colors capitalize',
          activeTab === tab
            ? 'bg-accent-blue/20 text-accent-blue'
            : 'text-surface-mid hover:text-surface-light',
        ]"
        @click="switchTab(tab)"
      >
        {{ tab }}
      </button>
    </div>

    <div v-if="activeTab === 'transactions'" class="flex flex-col gap-6">
      <ExpenseQuickAdd
        v-model:category="quickAdd.category"
        v-model:product="quickAdd.product"
        v-model:price="quickAdd.price"
        :loading="loading"
        :category-options="categoryOptions"
        :currency-label="quickAddCurrency"
        @submit="quickSaveExpense"
      />

      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1">
          <BaseInput v-model="productFilter" placeholder="Filter by product..." />
        </div>
        <div class="flex gap-2 items-end">
          <select
            v-model="categoryFilter"
            class="bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light font-mono text-sm focus:outline-none focus:border-accent-blue transition-colors h-[42px]"
          >
            <option :value="null">All categories</option>
            <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
          </select>
          <BaseButton variant="primary" @click="openCreate">+ Add</BaseButton>
        </div>
      </div>

      <p class="text-xs text-surface-mid font-mono -mt-3">{{ expenseCountLabel }}</p>

      <ExpenseList
        :expenses="expenses"
        :loading="listLoading"
        :month-label="monthLabel"
        :display-currency="displayCurrency as CurrencyCode"
        :exchange-rates="exchangeRates"
        :format-money="formatMoney"
        :format-expense-date="formatExpenseDate"
        :convert-amount="convertAmount"
        @edit="openEdit"
        @delete="requestDeleteExpense"
      />
    </div>

    <ExpenseInsights
      v-else-if="activeTab === 'insights'"
      :has-chart-data="hasChartData"
      :line-chart="lineChart"
      :bar-chart="barChart"
      :doughnut-chart="doughnutChart"
    />

    <ExpenseCategorySettings
      v-else
      v-model:display-currency="displayCurrency"
      v-model:new-category-name="newCategoryName"
      v-model:editing-category-name="editingCategoryName"
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
