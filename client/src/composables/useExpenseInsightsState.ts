import type { useExpenseSummary } from "@/composables/useExpenseSummary";

type ExpenseSummaryHook = ReturnType<typeof useExpenseSummary>;

/**
 * Insights-facing slice of shared expense summary state.
 *
 * Chart/summary data and loaders live in `useExpenseSummary`; the insights UI lives in
 * `ExpenseInsights.vue`. This helper only picks the props the insights tab (and ledger
 * header summary card) need — there is no separate insights-only store.
 */
export function useExpenseInsightsState(summaryHook: ExpenseSummaryHook) {
  const {
    summary,
    periodChange,
    exchangeRates,
    lineChart,
    barChart,
    doughnutChart,
    hasChartData,
    convertAmount,
    formatMoney,
    summaryError,
    ratesError,
    loadSummary,
    loadRates,
  } = summaryHook;

  return {
    summary,
    periodChange,
    exchangeRates,
    lineChart,
    barChart,
    doughnutChart,
    hasChartData,
    convertAmount,
    formatMoney,
    summaryError,
    ratesError,
    loadSummary,
    loadRates,
  };
}
