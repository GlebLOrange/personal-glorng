<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import ExpenseBarChart from "@/components/charts/ExpenseBarChart.vue";
import ExpenseDoughnutChart from "@/components/charts/ExpenseDoughnutChart.vue";
import ExpenseLineChart from "@/components/charts/ExpenseLineChart.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import type { ExchangeRates, ExpenseCategory, ToolExpense, ToolExpenseSummary } from "@/types";

type MonthPreset = "this_month" | "last_month" | "custom";
type CurrencyCode = "USD" | "EUR" | "PLN" | "BYN";

const CURRENCY_STORAGE_KEY = "expense_default_currency";
const currencies: CurrencyCode[] = ["USD", "EUR", "PLN", "BYN"];

const expenses = ref<ToolExpense[]>([]);
const summary = ref<ToolExpenseSummary | null>(null);
const expenseCategories = ref<ExpenseCategory[]>([]);
const showCategoryManager = ref(false);
const newCategoryName = ref("");
const editingCategoryId = ref<number | null>(null);
const editingCategoryName = ref("");
const monthPreset = ref<MonthPreset>("this_month");
const selectedMonth = ref("");
const productFilter = ref("");
const categoryFilter = ref<string | null>(null);
const loading = ref(false);
const showForm = ref(false);
const editingId = ref<number | null>(null);
const showCharts = ref(false);
const exchangeRates = ref<ExchangeRates | null>(null);

const quickAdd = ref({
  price: "",
  category: "Groceries",
  product: "",
});

const categoryOptions = computed(() =>
  expenseCategories.value.map((category) => category.name),
);

const defaultCategoryName = computed(
  () => categoryOptions.value.find((name) => name === "Groceries") ?? categoryOptions.value[0] ?? "Groceries",
);

const selectClass =
  "bg-surface-dark border border-surface-border rounded-lg px-3 py-2 text-surface-light font-mono text-sm "
  + "focus:outline-none focus:border-accent-blue transition-colors h-[42px]";
const selectClassCompact =
  "bg-surface-dark border border-surface-border rounded-lg px-2 py-1.5 text-surface-light font-mono text-xs "
  + "focus:outline-none focus:border-accent-blue transition-colors h-[34px] min-w-[7.5rem]";

function loadDefaultCurrency(): CurrencyCode {
  const stored = localStorage.getItem(CURRENCY_STORAGE_KEY);
  if (stored && currencies.includes(stored as CurrencyCode)) {
    return stored as CurrencyCode;
  }
  return "PLN";
}

const displayCurrency = ref<CurrencyCode>(loadDefaultCurrency());

const form = ref({
  tool_name: "",
  amount: "",
  currency: loadDefaultCurrency(),
  expense_date: new Date().toISOString().slice(0, 10),
  category: "",
  notes: "",
});

const { toast } = useNotify();

const formTitle = computed(() => (editingId.value ? "edit expense" : "new expense"));

const monthLabel = computed(() => {
  if (!selectedMonth.value) return "";
  const [year, month] = selectedMonth.value.split("-").map(Number);
  return new Date(year, month - 1, 1).toLocaleDateString("en-GB", {
    month: "long",
    year: "numeric",
  });
});

function currentMonthValue(d = new Date()): string {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  return `${year}-${month}`;
}

function applyMonthPreset(preset: MonthPreset): void {
  monthPreset.value = preset;
  if (preset === "custom") return;

  const today = new Date();
  if (preset === "this_month") {
    selectedMonth.value = currentMonthValue(today);
    return;
  }

  const prev = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  selectedMonth.value = currentMonthValue(prev);
}

function queryParams(): Record<string, string> {
  const params: Record<string, string> = {};
  if (selectedMonth.value) params.month = selectedMonth.value;
  if (productFilter.value.trim()) {
    params.tool_name = productFilter.value.trim();
  }
  if (categoryFilter.value) params.category = categoryFilter.value;
  return params;
}

function summaryParams(): Record<string, string> {
  return { ...queryParams(), display_currency: displayCurrency.value };
}

function convertAmount(amount: string, from: CurrencyCode, to: CurrencyCode): number {
  if (from === to || !exchangeRates.value) return parseFloat(amount);
  const rates = exchangeRates.value.rates;
  const usd = parseFloat(amount) / parseFloat(rates[from]);
  return usd * parseFloat(rates[to]);
}

function formatMoney(amount: string | number, currency: string): string {
  const value = typeof amount === "string" ? parseFloat(amount) : amount;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(value);
}

function formatExpenseDate(iso: string): string {
  return new Date(iso + "T00:00:00").toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function topCategoryChart(
  summaryData: ToolExpenseSummary,
): { labels: string[]; values: number[] } {
  const items = summaryData.by_category.map((c) => ({
    label: c.category,
    value: parseFloat(c.total),
  }));
  if (items.length <= 8) {
    return { labels: items.map((i) => i.label), values: items.map((i) => i.value) };
  }
  const top = items.slice(0, 7);
  const other = items.slice(7).reduce((sum, i) => sum + i.value, 0);
  return {
    labels: [...top.map((i) => i.label), "Other"],
    values: [...top.map((i) => i.value), other],
  };
}

function topDescriptionChart(
  summaryData: ToolExpenseSummary,
): { labels: string[]; values: number[] } {
  const items = summaryData.by_tool.map((t) => ({
    label: t.tool_name,
    value: parseFloat(t.total),
  }));
  if (items.length <= 6) {
    return { labels: items.map((i) => i.label), values: items.map((i) => i.value) };
  }
  const top = items.slice(0, 5);
  const other = items.slice(5).reduce((sum, i) => sum + i.value, 0);
  return {
    labels: [...top.map((i) => i.label), "Other"],
    values: [...top.map((i) => i.value), other],
  };
}

const lineChart = computed(() => {
  if (!summary.value) return { labels: [] as string[], values: [] as number[] };
  return {
    labels: summary.value.by_month.map((m) => m.period),
    values: summary.value.by_month.map((m) => parseFloat(m.total)),
  };
});

const barChart = computed(() => {
  if (!summary.value) return { labels: [] as string[], values: [] as number[] };
  return topCategoryChart(summary.value);
});

const doughnutChart = computed(() => {
  if (!summary.value) return { labels: [] as string[], values: [] as number[] };
  return topDescriptionChart(summary.value);
});

const hasChartData = computed(
  () =>
  (summary.value?.by_month.length ?? 0) > 0
    || (summary.value?.by_tool.length ?? 0) > 0
    || (summary.value?.by_category.length ?? 0) > 0,
);

const quickAddCurrency = computed(() => loadDefaultCurrency());

function resetForm(): void {
  form.value = {
    tool_name: "",
    amount: "",
    currency: loadDefaultCurrency(),
    expense_date: new Date().toISOString().slice(0, 10),
    category: defaultCategoryName.value,
    notes: "",
  };
  editingId.value = null;
}

function resetQuickAdd(): void {
  quickAdd.value = {
    price: "",
    category: defaultCategoryName.value,
    product: "",
  };
}

async function loadExpenses(): Promise<void> {
  try {
    const { data } = await api.get<ToolExpense[]>("/tools/expenses", { params: queryParams() });
    expenses.value = data;
  } catch (err) {
    console.error(err);
    toast("Failed to load expenses", "error");
  }
}

async function loadRates(): Promise<void> {
  try {
    const { data } = await api.get<ExchangeRates>("/tools/expenses/rates");
    exchangeRates.value = data;
  } catch (err) {
    console.error(err);
    toast("Failed to load exchange rates", "error");
  }
}

async function loadSummary(): Promise<void> {
  try {
    const { data } = await api.get<ToolExpenseSummary>("/tools/expenses/summary", {
      params: summaryParams(),
    });
    summary.value = data;
  } catch (err) {
    console.error(err);
    toast("Failed to load summary", "error");
  }
}

async function loadCategories(): Promise<void> {
  try {
    const { data } = await api.get<ExpenseCategory[]>("/tools/expenses/categories");
    expenseCategories.value = data;
  } catch (err) {
    console.error(err);
  }
}

async function addCategory(): Promise<void> {
  const name = newCategoryName.value.trim();
  if (!name) {
    toast("Category name is required", "error");
    return;
  }

  try {
    await api.post("/tools/expenses/categories", { name });
    newCategoryName.value = "";
    toast("Category added", "success");
    await loadCategories();
  } catch (err) {
    console.error(err);
    toast("Failed to add category", "error");
  }
}

function startEditCategory(category: ExpenseCategory): void {
  editingCategoryId.value = category.id;
  editingCategoryName.value = category.name;
}

function cancelEditCategory(): void {
  editingCategoryId.value = null;
  editingCategoryName.value = "";
}

async function saveCategoryRename(): Promise<void> {
  if (editingCategoryId.value === null) return;
  const name = editingCategoryName.value.trim();
  if (!name) {
    toast("Category name is required", "error");
    return;
  }

  try {
    await api.put(`/tools/expenses/categories/${editingCategoryId.value}`, { name });
    cancelEditCategory();
    toast("Category updated", "success");
    await Promise.all([loadCategories(), loadExpenses(), loadSummary()]);
  } catch (err) {
    console.error(err);
    toast("Failed to update category", "error");
  }
}

async function removeCategory(category: ExpenseCategory): Promise<void> {
  if (!confirm(`Delete category "${category.name}"?`)) return;

  try {
    await api.delete(`/tools/expenses/categories/${category.id}`);
    toast("Category deleted", "success");
    await loadCategories();
  } catch (err) {
    console.error(err);
    toast("Cannot delete a category that is used by expenses", "error");
  }
}

async function reloadAfterMutation(): Promise<void> {
  await Promise.all([loadExpenses(), loadSummary(), loadCategories()]);
}

async function reloadOnMonthChange(): Promise<void> {
  await Promise.all([loadExpenses(), loadSummary()]);
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
  localStorage.setItem(CURRENCY_STORAGE_KEY, payload.currency);
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

  const toolName = form.value.tool_name.trim();

  loading.value = true;
  const payload = {
    tool_name: toolName,
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
    toast("Failed to save expense", "error");
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

  const currency = loadDefaultCurrency();
  const toolName = product;
  const payload = {
    tool_name: toolName,
    amount: amount.toFixed(2),
    currency,
    expense_date: new Date().toISOString().slice(0, 10),
    category: quickAdd.value.category,
    notes: null,
  };

  loading.value = true;
  try {
    await postExpense(payload);
    resetQuickAdd();
    await reloadAfterMutation();
  } catch (err) {
    console.error(err);
    toast("Failed to save expense", "error");
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
  form.value.category = defaultCategoryName.value;
  showForm.value = true;
}

async function deleteExpense(id: number): Promise<void> {
  if (!confirm("Delete this expense?")) return;

  try {
    await api.delete(`/tools/expenses/${id}`);
    toast("Expense deleted", "success");
    await reloadAfterMutation();
  } catch (err) {
    console.error(err);
    toast("Failed to delete expense", "error");
  }
}

let debounceTimer: ReturnType<typeof setTimeout>;
watch(productFilter, () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(loadExpenses, 300);
});

watch([selectedMonth, categoryFilter], reloadOnMonthChange);
watch(displayCurrency, (value) => {
  localStorage.setItem(CURRENCY_STORAGE_KEY, value);
  loadSummary();
});

watch(selectedMonth, () => {
  if (monthPreset.value !== "custom") return;
});

onMounted(() => {
  applyMonthPreset("this_month");
  displayCurrency.value = loadDefaultCurrency();
  void Promise.all([loadRates(), reloadOnMonthChange(), loadCategories()]);
});
</script>

<template>
  <AdminPageLayout title="monthly expenses" max-width="xl">
  <div class="flex flex-col gap-4 mb-6">
    <div class="flex flex-wrap gap-2 items-center">
      <BaseButton
        v-for="preset in (['this_month', 'last_month', 'custom'] as MonthPreset[])"
        :key="preset"
        :variant="monthPreset === preset ? 'primary' : 'ghost'"
        size="sm"
        @click="applyMonthPreset(preset)"
      >
        {{ preset === "this_month" ? "This month" : preset === "last_month" ? "Last month" : "Custom" }}
      </BaseButton>
      <input
        v-model="selectedMonth"
        type="month"
        class="bg-surface-dark border border-surface-border rounded-lg px-3 py-1.5 text-surface-light font-mono text-sm
               focus:outline-none focus:border-accent-blue h-[34px]"
        @change="monthPreset = 'custom'"
      >
    </div>

    <BaseCard class="flex flex-col gap-4">
      <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <p class="text-xs text-surface-mid font-mono uppercase tracking-wider">
            Total for {{ monthLabel }}
          </p>
          <p v-if="summary" class="text-2xl font-bold text-surface-light">
            {{ formatMoney(summary.total, summary.currency) }}
          </p>
          <p v-if="summary?.rates_updated_at" class="text-[10px] text-surface-mid font-mono mt-1">
            FX via Exchange Rate API · {{ summary.rates_updated_at }}
          </p>
        </div>
        <div>
          <label class="text-sm text-surface-mid font-mono block mb-1">Show totals in</label>
          <select
            v-model="displayCurrency"
            class="bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light font-mono text-sm
                   focus:outline-none focus:border-accent-blue transition-colors h-[42px]"
          >
            <option v-for="c in currencies" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
      </div>
      <div
        v-if="exchangeRates"
        class="flex flex-wrap gap-3 text-xs font-mono text-surface-mid border-t border-surface-border pt-3"
      >
        <span class="text-surface-light">1 USD =</span>
        <span v-for="c in currencies.filter((code) => code !== 'USD')" :key="c">
          {{ parseFloat(exchangeRates.rates[c]).toFixed(4) }} {{ c }}
        </span>
      </div>
    </BaseCard>
  </div>

  <!-- Quick add -->
  <BaseCard class="sticky top-4 z-10 mb-6">
    <p class="text-xs text-surface-mid font-mono uppercase tracking-wider mb-3">Quick add</p>
    <form class="flex flex-col gap-2" @submit.prevent="quickSaveExpense">
      <div class="flex flex-col sm:flex-row sm:items-end gap-3">
        <div>
          <label class="text-[10px] text-surface-mid font-mono uppercase tracking-wider block mb-1">
            Category
          </label>
          <select v-model="quickAdd.category" :class="selectClassCompact">
            <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
        <div class="flex-1">
          <BaseInput v-model="quickAdd.product" label="Product" placeholder="Milk, fuel, rent..." />
        </div>
        <div class="sm:w-28">
          <BaseInput
            v-model="quickAdd.price"
            label="Price"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="0.00"
          />
        </div>
        <BaseButton variant="primary" type="submit" :disabled="loading" class="sm:mb-0.5">
          {{ loading ? "Saving..." : "Save" }}
        </BaseButton>
      </div>
      <p class="text-[10px] text-surface-mid font-mono">
        {{ quickAddCurrency }} · today · full form for date, currency, notes
      </p>
    </form>
  </BaseCard>

  <!-- Category manager -->
  <BaseCard class="mb-6">
    <div class="flex items-center justify-between gap-3 mb-3">
      <p class="text-xs text-surface-mid font-mono uppercase tracking-wider">Categories</p>
      <BaseButton variant="ghost" size="sm" @click="showCategoryManager = !showCategoryManager">
        {{ showCategoryManager ? "Hide" : "Edit" }}
      </BaseButton>
    </div>

    <div v-if="showCategoryManager" class="flex flex-col gap-3">
      <ul class="divide-y divide-surface-border rounded-lg border border-surface-border">
        <li
          v-for="category in expenseCategories"
          :key="category.id"
          class="flex flex-wrap items-center gap-2 px-3 py-2"
        >
          <template v-if="editingCategoryId === category.id">
            <input
              v-model="editingCategoryName"
              class="flex-1 min-w-[8rem] bg-surface-dark border border-surface-border rounded-lg px-3 py-1.5
                     text-surface-light font-mono text-sm focus:outline-none focus:border-accent-blue"
              @keyup.enter="saveCategoryRename"
            >
            <BaseButton variant="primary" size="sm" @click="saveCategoryRename">Save</BaseButton>
            <BaseButton variant="ghost" size="sm" @click="cancelEditCategory">Cancel</BaseButton>
          </template>
          <template v-else>
            <span class="flex-1 text-surface-light font-mono text-sm">{{ category.name }}</span>
            <BaseButton variant="ghost" size="sm" @click="startEditCategory(category)">Rename</BaseButton>
            <BaseButton variant="ghost" size="sm" @click="removeCategory(category)">Delete</BaseButton>
          </template>
        </li>
      </ul>

      <form class="flex flex-col sm:flex-row gap-2" @submit.prevent="addCategory">
        <input
          v-model="newCategoryName"
          placeholder="New category name"
          class="flex-1 bg-surface-dark border border-surface-border rounded-lg px-3 py-2 text-surface-light
                 font-mono text-sm focus:outline-none focus:border-accent-blue h-[42px]"
        >
        <BaseButton variant="primary" type="submit">Add category</BaseButton>
      </form>
      <p class="text-[10px] text-surface-mid font-mono">
        Renaming updates all expenses in that category. Delete only works when unused.
      </p>
    </div>
  </BaseCard>

  <!-- Charts -->
  <div v-if="hasChartData" class="mb-4">
    <BaseButton variant="ghost" size="sm" @click="showCharts = !showCharts">
      {{ showCharts ? "Hide charts" : "Show charts" }}
    </BaseButton>
  </div>
  <div v-if="hasChartData && showCharts" class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
    <BaseCard>
      <h3 class="text-xs font-mono text-surface-mid uppercase tracking-wider mb-3">Monthly trend</h3>
      <ExpenseLineChart :labels="lineChart.labels" :values="lineChart.values" />
    </BaseCard>
    <BaseCard>
      <h3 class="text-xs font-mono text-surface-mid uppercase tracking-wider mb-3">By category</h3>
      <ExpenseBarChart :labels="barChart.labels" :values="barChart.values" />
    </BaseCard>
    <BaseCard>
      <h3 class="text-xs font-mono text-surface-mid uppercase tracking-wider mb-3">By product</h3>
      <ExpenseDoughnutChart :labels="doughnutChart.labels" :values="doughnutChart.values" />
    </BaseCard>
  </div>

  <!-- Filters -->
  <div class="flex flex-col sm:flex-row gap-3 mb-6">
    <div class="flex-1">
      <BaseInput v-model="productFilter" placeholder="Filter by product..." />
    </div>
    <div class="flex gap-2 items-end">
      <select
        v-model="categoryFilter"
        class="bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light font-mono text-sm
               focus:outline-none focus:border-accent-blue transition-colors h-[42px]"
      >
        <option :value="null">All categories</option>
        <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
      </select>
      <BaseButton variant="primary" @click="openCreate">+ Add</BaseButton>
    </div>
  </div>

  <!-- Form modal -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="showForm"
        class="fixed inset-0 z-50 flex items-start justify-center pt-16 px-4 bg-black/60"
        @click.self="showForm = false"
      >
        <div class="bg-surface-card border border-surface-border rounded-lg p-6 w-full max-w-lg max-h-[80vh] overflow-y-auto">
          <h2 class="text-lg font-bold text-surface-light mb-6">
            <span class="accent-gradient">€ {{ formTitle }}</span>
          </h2>

          <form class="space-y-4" @submit.prevent="saveExpense">
            <div>
              <label class="text-sm text-surface-mid font-mono block mb-1">Category</label>
              <select v-model="form.category" :class="[selectClass, 'w-full']">
                <option value="">—</option>
                <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <BaseInput
                v-model="form.tool_name"
                label="Product"
                placeholder="Milk, dinner, Shell..."
              />
              <BaseInput
                v-model="form.amount"
                label="Price"
                type="number"
                step="0.01"
                min="0.01"
                placeholder="20.00"
              />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <BaseInput v-model="form.expense_date" label="Date" type="date" />
              <div>
                <label class="text-sm text-surface-mid font-mono block mb-1">Currency</label>
                <select v-model="form.currency" :class="[selectClass, 'w-full']">
                  <option v-for="c in currencies" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>
            </div>

            <div>
              <label class="text-sm text-surface-mid font-mono block mb-1">Notes</label>
              <textarea
                v-model="form.notes"
                rows="3"
                placeholder="Invoice ref, billing period..."
                class="w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light font-mono text-sm
                       focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50 resize-none"
              />
            </div>

            <div class="flex gap-3 pt-2">
              <BaseButton variant="primary" :disabled="loading">
                {{ loading ? "Saving..." : "Save" }}
              </BaseButton>
              <BaseButton variant="ghost" type="button" @click="showForm = false">
                Cancel
              </BaseButton>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- Transaction table -->
  <div class="overflow-x-auto rounded-lg border border-surface-border">
    <table class="w-full text-sm font-mono">
      <thead>
        <tr class="text-left text-surface-mid border-b border-surface-border bg-surface-card">
          <th class="px-4 py-3">Date</th>
          <th class="px-4 py-3">Category</th>
          <th class="px-4 py-3">Product</th>
          <th class="px-4 py-3 text-right">Price</th>
          <th class="px-4 py-3">Notes</th>
          <th class="px-4 py-3 text-right">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="expense in expenses"
          :key="expense.id"
          class="border-b border-surface-border/60 text-surface-light hover:bg-surface-card/50"
        >
          <td class="px-4 py-3 whitespace-nowrap">{{ formatExpenseDate(expense.expense_date) }}</td>
          <td class="px-4 py-3 text-surface-mid">{{ expense.category ?? "—" }}</td>
          <td class="px-4 py-3">{{ expense.tool_name }}</td>
          <td class="px-4 py-3 text-right whitespace-nowrap">
            <div>{{ formatMoney(expense.amount, expense.currency) }}</div>
            <div
              v-if="expense.currency !== displayCurrency && exchangeRates"
              class="text-[10px] text-surface-mid"
            >
              ≈ {{ formatMoney(
                convertAmount(expense.amount, expense.currency as CurrencyCode, displayCurrency),
                displayCurrency,
              ) }}
            </div>
          </td>
          <td class="px-4 py-3 text-surface-mid max-w-[200px] truncate">{{ expense.notes ?? "—" }}</td>
          <td class="px-4 py-3 text-right whitespace-nowrap">
            <BaseButton variant="ghost" size="sm" @click="openEdit(expense)">Edit</BaseButton>
            <BaseButton variant="ghost" size="sm" @click="deleteExpense(expense.id)">Delete</BaseButton>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <p v-if="expenses.length === 0" class="text-surface-mid text-sm text-center py-8">
    No expenses in this period. Add your first charge above.
  </p>
  </AdminPageLayout>
</template>
