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
import type { ExchangeRates, ToolExpense, ToolExpenseSummary } from "@/types";

type DatePreset = "30d" | "ytd" | "12m" | "all";
type CurrencyCode = "USD" | "EUR" | "PLN" | "BYN";

const expenses = ref<ToolExpense[]>([]);
const summary = ref<ToolExpenseSummary | null>(null);
const categories = ref<string[]>([]);
const datePreset = ref<DatePreset>("12m");
const dateFrom = ref("");
const dateTo = ref("");
const toolFilter = ref("");
const categoryFilter = ref<string | null>(null);
const loading = ref(false);
const showForm = ref(false);
const editingId = ref<number | null>(null);
const displayCurrency = ref<CurrencyCode>("USD");
const exchangeRates = ref<ExchangeRates | null>(null);

const form = ref({
  tool_name: "",
  amount: "",
  currency: "USD" as CurrencyCode,
  expense_date: new Date().toISOString().slice(0, 10),
  category: "",
  notes: "",
});

const { toast } = useNotify();

const formTitle = computed(() => (editingId.value ? "edit expense" : "new expense"));

const currencies: CurrencyCode[] = ["USD", "EUR", "PLN", "BYN"];

function toIsoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function applyPreset(preset: DatePreset): void {
  datePreset.value = preset;
  const today = new Date();
  const end = toIsoDate(today);

  if (preset === "all") {
    dateFrom.value = "";
    dateTo.value = "";
    return;
  }

  dateTo.value = end;
  const start = new Date(today);

  if (preset === "30d") {
    start.setDate(start.getDate() - 30);
  } else if (preset === "ytd") {
    start.setMonth(0, 1);
  } else {
    start.setFullYear(start.getFullYear() - 1);
  }

  dateFrom.value = toIsoDate(start);
}

function queryParams(): Record<string, string> {
  const params: Record<string, string> = {};
  if (dateFrom.value) params.date_from = dateFrom.value;
  if (dateTo.value) params.date_to = dateTo.value;
  if (toolFilter.value.trim()) params.tool_name = toolFilter.value.trim();
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

function topToolChart(summaryData: ToolExpenseSummary): { labels: string[]; values: number[] } {
  const items = summaryData.by_tool.map((t) => ({
    label: t.tool_name,
    value: parseFloat(t.total),
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

const lineChart = computed(() => {
  if (!summary.value) return { labels: [] as string[], values: [] as number[] };
  return {
    labels: summary.value.by_month.map((m) => m.period),
    values: summary.value.by_month.map((m) => parseFloat(m.total)),
  };
});

const barChart = computed(() => {
  if (!summary.value) return { labels: [] as string[], values: [] as number[] };
  return topToolChart(summary.value);
});

const doughnutChart = computed(() => {
  if (!summary.value) return { labels: [] as string[], values: [] as number[] };
  return {
    labels: summary.value.by_category.map((c) => c.category),
    values: summary.value.by_category.map((c) => parseFloat(c.total)),
  };
});

const hasChartData = computed(
  () =>
  (summary.value?.by_month.length ?? 0) > 0
    || (summary.value?.by_tool.length ?? 0) > 0
    || (summary.value?.by_category.length ?? 0) > 0,
);

function resetForm(): void {
  form.value = {
    tool_name: "",
    amount: "",
    currency: "USD" as CurrencyCode,
    expense_date: new Date().toISOString().slice(0, 10),
    category: "",
    notes: "",
  };
  editingId.value = null;
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
    const { data } = await api.get<string[]>("/tools/expenses/categories");
    categories.value = data;
  } catch (err) {
    console.error(err);
  }
}

async function reloadAll(): Promise<void> {
  await Promise.all([loadExpenses(), loadSummary(), loadCategories(), loadRates()]);
}

async function saveExpense(): Promise<void> {
  if (!form.value.tool_name.trim() || !form.value.amount || !form.value.expense_date) return;
  const amount = parseFloat(form.value.amount);
  if (Number.isNaN(amount) || amount <= 0) {
    toast("Amount must be greater than zero", "error");
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
    if (editingId.value) {
      await api.put(`/tools/expenses/${editingId.value}`, payload);
      toast("Expense updated", "success");
    } else {
      await api.post("/tools/expenses", payload);
      toast("Expense created", "success");
    }
    showForm.value = false;
    resetForm();
    await reloadAll();
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
  showForm.value = true;
}

async function deleteExpense(id: number): Promise<void> {
  try {
    await api.delete(`/tools/expenses/${id}`);
    toast("Expense deleted", "success");
    await reloadAll();
  } catch (err) {
    console.error(err);
    toast("Failed to delete expense", "error");
  }
}

let debounceTimer: ReturnType<typeof setTimeout>;
watch(toolFilter, () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(reloadAll, 300);
});

watch([dateFrom, dateTo, categoryFilter], reloadAll);
watch(displayCurrency, () => {
  loadSummary();
});

onMounted(() => {
  applyPreset("12m");
  reloadAll();
});
</script>

<template>
  <AdminPageLayout title="tool expenses" max-width="xl">
  <!-- Date presets & summary -->
  <div class="flex flex-col gap-4 mb-6">
    <div class="flex flex-wrap gap-2">
      <BaseButton
        v-for="preset in (['30d', 'ytd', '12m', 'all'] as DatePreset[])"
        :key="preset"
        :variant="datePreset === preset ? 'primary' : 'ghost'"
        size="sm"
        @click="applyPreset(preset)"
      >
        {{ preset === "30d" ? "Last 30 days" : preset === "ytd" ? "YTD" : preset === "12m" ? "Last 12 months" : "All time" }}
      </BaseButton>
    </div>

    <BaseCard class="flex flex-col gap-4">
      <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <p class="text-xs text-surface-mid font-mono uppercase tracking-wider">Total spending</p>
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

  <!-- Charts -->
  <div v-if="hasChartData" class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
    <BaseCard>
      <h3 class="text-xs font-mono text-surface-mid uppercase tracking-wider mb-3">Monthly trend</h3>
      <ExpenseLineChart :labels="lineChart.labels" :values="lineChart.values" />
    </BaseCard>
    <BaseCard>
      <h3 class="text-xs font-mono text-surface-mid uppercase tracking-wider mb-3">By tool</h3>
      <ExpenseBarChart :labels="barChart.labels" :values="barChart.values" />
    </BaseCard>
    <BaseCard>
      <h3 class="text-xs font-mono text-surface-mid uppercase tracking-wider mb-3">By category</h3>
      <ExpenseDoughnutChart :labels="doughnutChart.labels" :values="doughnutChart.values" />
    </BaseCard>
  </div>

  <!-- Filters -->
  <div class="flex flex-col sm:flex-row gap-3 mb-6">
    <div class="flex-1">
      <BaseInput v-model="toolFilter" placeholder="Filter by tool name..." />
    </div>
    <div class="flex gap-2 items-end">
      <select
        v-model="categoryFilter"
        class="bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light font-mono text-sm
               focus:outline-none focus:border-accent-blue transition-colors h-[42px]"
      >
        <option :value="null">All categories</option>
        <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
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
            <BaseInput v-model="form.tool_name" label="Tool / vendor" placeholder="Cursor, Vercel..." />

            <div class="grid grid-cols-2 gap-3">
              <BaseInput
                v-model="form.amount"
                label="Amount"
                type="number"
                step="0.01"
                min="0.01"
                placeholder="20.00"
              />
              <div>
                <label class="text-sm text-surface-mid font-mono block mb-1">Currency</label>
                <select
                  v-model="form.currency"
                  class="w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light font-mono text-sm
                         focus:outline-none focus:border-accent-blue transition-colors h-[42px]"
                >
                  <option v-for="c in currencies" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>
            </div>

            <BaseInput v-model="form.expense_date" label="Date" type="date" />

            <BaseInput
              v-model="form.category"
              label="Category"
              placeholder="AI, Hosting, APIs..."
              list="expense-categories"
            />
            <datalist id="expense-categories">
              <option v-for="cat in categories" :key="cat" :value="cat" />
            </datalist>

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
          <th class="px-4 py-3">Tool</th>
          <th class="px-4 py-3">Category</th>
          <th class="px-4 py-3 text-right">Amount</th>
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
          <td class="px-4 py-3">{{ expense.tool_name }}</td>
          <td class="px-4 py-3 text-surface-mid">{{ expense.category ?? "—" }}</td>
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
