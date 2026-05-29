import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import type { ExchangeRates, ToolExpense, ToolExpenseSummary } from "@/types";

import type { CurrencyCode } from "./useExpenseFilters";

function topCategoryChart(summaryData: ToolExpenseSummary): { labels: string[]; values: number[] } {
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

function topDescriptionChart(summaryData: ToolExpenseSummary): {
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
) {
  const expenses = ref<ToolExpense[]>([]);
  const summary = ref<ToolExpenseSummary | null>(null);
  const exchangeRates = ref<ExchangeRates | null>(null);
  const { toast } = useNotify();

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

  async function loadExpenses(): Promise<void> {
    try {
      const { data } = await api.get<ToolExpense[]>("/tools/expenses", {
        params: queryParams(),
      });
      expenses.value = data;
    } catch (err) {
      console.error(err);
      toast(getApiErrorMessage(err, "Failed to load expenses"), "error");
    }
  }

  async function loadRates(): Promise<void> {
    try {
      const { data } = await api.get<ExchangeRates>("/tools/expenses/rates");
      exchangeRates.value = data;
    } catch (err) {
      console.error(err);
      toast(getApiErrorMessage(err, "Failed to load exchange rates"), "error");
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
      toast(getApiErrorMessage(err, "Failed to load summary"), "error");
    }
  }

  async function reloadListAndSummary(): Promise<void> {
    await Promise.all([loadExpenses(), loadSummary()]);
  }

  return {
    expenses,
    summary,
    exchangeRates,
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
  };
}
