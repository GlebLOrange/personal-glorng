import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import type { ExchangeRates, Expense, ExpenseSummary, PaginatedExpenses } from "@/types";

import type { CurrencyCode } from "./useExpenseFilters";

function topCategoryChart(summaryData: ExpenseSummary): { labels: string[]; values: number[] } {
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

function topDescriptionChart(summaryData: ExpenseSummary): {
  labels: string[];
  values: number[];
} {
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

export function useExpenseSummary(
  queryParams: () => Record<string, string>,
  summaryParams: () => Record<string, string>,
  previousSummaryParams: () => Record<string, string>,
) {
  const expenses = ref<Expense[]>([]);
  const expenseTotal = ref(0);
  const expensePage = ref(1);
  const expensePages = ref(0);
  const expensePerPage = ref(20);
  const summary = ref<ExpenseSummary | null>(null);
  const previousSummary = ref<ExpenseSummary | null>(null);
  const exchangeRates = ref<ExchangeRates | null>(null);
  const listLoading = ref(false);
  const listError = ref<string | null>(null);
  const summaryError = ref<string | null>(null);
  const ratesError = ref<string | null>(null);
  const { toast } = useNotify();

  const periodChange = computed(() => {
    if (!summary.value || !previousSummary.value) return null;
    const current = parseFloat(String(summary.value.total));
    const previous = parseFloat(String(previousSummary.value.total));
    if (previous <= 0) return null;
    const delta = Math.round(((current - previous) / previous) * 100);
    return { delta, increased: delta > 0 };
  });

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
      (summary.value?.by_month.length ?? 0) > 0 ||
      (summary.value?.by_tool.length ?? 0) > 0 ||
      (summary.value?.by_category.length ?? 0) > 0,
  );

  function convertAmount(amount: string, from: CurrencyCode, to: CurrencyCode): number {
    const value = parseFloat(amount);
    if (from === to || !exchangeRates.value) return value;
    const rates = exchangeRates.value.rates;
    const fromRate = parseFloat(rates[from]);
    const toRate = parseFloat(rates[to]);
    if (
      !Number.isFinite(value) ||
      !Number.isFinite(fromRate) ||
      !Number.isFinite(toRate) ||
      fromRate === 0
    ) {
      return Number.NaN;
    }
    return (value / fromRate) * toRate;
  }

  function formatMoney(amount: string | number, currency: string): string {
    const value = typeof amount === "string" ? parseFloat(amount) : amount;
    if (!Number.isFinite(value)) return "N/A";
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

  async function loadExpenses(): Promise<void> {
    listLoading.value = true;
    try {
      const { data } = await api.get<PaginatedExpenses>("/tools/expenses", {
        params: queryParams(),
      });
      expenses.value = data.items;
      expenseTotal.value = data.total;
      expensePage.value = data.page;
      expensePages.value = data.pages;
      expensePerPage.value = data.per_page;
      listError.value = null;
    } catch (err) {
      if (import.meta.env.DEV) console.error(err);
      const message = getApiErrorMessage(err, "Failed to load expenses");
      listError.value = message;
      toast(message, "error");
    } finally {
      listLoading.value = false;
    }
  }

  async function loadRates(): Promise<void> {
    try {
      const { data } = await api.get<ExchangeRates>("/tools/expenses/rates");
      exchangeRates.value = data;
      ratesError.value = null;
    } catch (err) {
      if (import.meta.env.DEV) console.error(err);
      const message = getApiErrorMessage(err, "Failed to load exchange rates");
      ratesError.value = message;
      toast(message, "error");
    }
  }

  async function loadSummary(): Promise<void> {
    try {
      const { data } = await api.get<ExpenseSummary>("/tools/expenses/summary", {
        params: summaryParams(),
      });
      summary.value = data;
      summaryError.value = null;
    } catch (err) {
      if (import.meta.env.DEV) console.error(err);
      const message = getApiErrorMessage(err, "Failed to load summary");
      summaryError.value = message;
      toast(message, "error");
    }
  }

  async function loadPreviousSummary(): Promise<void> {
    const params = previousSummaryParams();
    if (!params.month && !params.date_from) {
      previousSummary.value = null;
      return;
    }

    try {
      const { data } = await api.get<ExpenseSummary>("/tools/expenses/summary", {
        params,
      });
      previousSummary.value = data;
    } catch (err) {
      if (import.meta.env.DEV) console.error(err);
      previousSummary.value = null;
      toast(getApiErrorMessage(err, "Failed to load period comparison"), "error");
    }
  }

  async function reloadListAndSummary(): Promise<void> {
    await Promise.all([loadExpenses(), loadSummary(), loadPreviousSummary()]);
  }

  return {
    expenses,
    expenseTotal,
    expensePage,
    expensePages,
    expensePerPage,
    summary,
    previousSummary,
    periodChange,
    exchangeRates,
    listLoading,
    listError,
    summaryError,
    ratesError,
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
  };
}
