<script setup lang="ts">
import { computed, defineAsyncComponent } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card } from "@/components/ui/card";
import type { ExpenseCategory, ExpenseSummary } from "@/types";

const ExpenseBarChart = defineAsyncComponent(() => import("@/components/charts/ExpenseBarChart.vue"));
const ExpenseDoughnutChart = defineAsyncComponent(
  () => import("@/components/charts/ExpenseDoughnutChart.vue"),
);
const ExpenseLineChart = defineAsyncComponent(() => import("@/components/charts/ExpenseLineChart.vue"));

const props = defineProps<{
  hasChartData: boolean;
  lineChart: { labels: string[]; values: number[] };
  barChart: { labels: string[]; values: number[] };
  doughnutChart: { labels: string[]; values: number[] };
  summary: ExpenseSummary | null;
  expenseCategories: ExpenseCategory[];
  formatMoney: (amount: string | number, currency: string) => string;
}>();

const emit = defineEmits<{
  addExpense: [];
}>();

const MAX_SERIES = 6;

function foldSeries(
  labels: string[],
  values: number[],
): { labels: string[]; values: number[]; rows: Array<{ label: string; value: number; percent: number }> } {
  const pairs = labels.map((label, i) => ({ label, value: values[i] ?? 0 }));
  pairs.sort((a, b) => b.value - a.value);
  const total = pairs.reduce((sum, p) => sum + p.value, 0);

  let folded = pairs;
  if (pairs.length > MAX_SERIES) {
    const head = pairs.slice(0, MAX_SERIES - 1);
    const other = pairs.slice(MAX_SERIES - 1).reduce((sum, p) => sum + p.value, 0);
    folded = [...head, { label: "Other", value: other }];
  }

  return {
    labels: folded.map((p) => p.label),
    values: folded.map((p) => p.value),
    rows: folded.map((p) => ({
      label: p.label,
      value: p.value,
      percent: total > 0 ? Math.round((p.value / total) * 100) : 0,
    })),
  };
}

const categorySeries = computed(() =>
  foldSeries(props.barChart.labels, props.barChart.values),
);
const productSeries = computed(() =>
  foldSeries(props.doughnutChart.labels, props.doughnutChart.values),
);

const showProductDoughnut = computed(
  () => productSeries.value.labels.length > 0 && productSeries.value.labels.length <= 5,
);

const budgetByCategory = computed(() => {
  const map = new Map<string, number>();
  for (const category of props.expenseCategories) {
    if (category.monthly_budget) {
      map.set(category.name, parseFloat(category.monthly_budget));
    }
  }
  return map;
});

const budgetRows = computed(() => {
  if (!props.summary) return [];
  return props.summary.by_category
    .map((item) => {
      const spent = parseFloat(String(item.total));
      const budget = budgetByCategory.value.get(item.category) ?? null;
      const percent = budget && budget > 0 ? Math.round((spent / budget) * 100) : null;
      return {
        category: item.category,
        spent,
        budget,
        percent,
        overBudget: percent !== null && percent > 100,
      };
    })
    .filter((row) => row.budget !== null);
});

const budgetTotals = computed(() => {
  if (!props.summary || budgetRows.value.length === 0) return null;
  const spent = budgetRows.value.reduce((sum, row) => sum + row.spent, 0);
  const budget = budgetRows.value.reduce((sum, row) => sum + (row.budget ?? 0), 0);
  if (budget <= 0) return null;
  const percent = Math.round((spent / budget) * 100);
  return { spent, budget, percent, overBudget: percent > 100 };
});

const currency = computed(() => props.summary?.currency ?? "PLN");
</script>

<template>
  <div v-if="hasChartData" class="flex flex-col gap-4">
    <Card v-if="budgetTotals" variant="compact">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h3 class="text-xs text-surface-mid">budget vs spend</h3>
          <p
            class="mt-1 text-xl font-bold font-data"
            :class="budgetTotals.overBudget ? 'text-status-error' : 'text-accent-blue'"
          >
            {{ budgetTotals.percent }}%
            <span class="sr-only">
              of budget{{ budgetTotals.overBudget ? ", over budget" : "" }}
            </span>
          </p>
          <p class="mt-1 text-xs text-surface-mid">
            {{ formatMoney(budgetTotals.spent, currency) }} of
            {{ formatMoney(budgetTotals.budget, currency) }}
          </p>
        </div>
        <div
          class="h-1.5 w-full max-w-xs overflow-hidden rounded-full bg-surface-border sm:mb-1"
          role="progressbar"
          :aria-valuenow="Math.min(budgetTotals.percent, 100)"
          aria-valuemin="0"
          aria-valuemax="100"
          :aria-label="`Budget used ${budgetTotals.percent}%`"
        >
          <div
            class="h-full rounded-full"
            :class="budgetTotals.overBudget ? 'bg-status-error' : 'bg-accent-blue'"
            :style="{ width: `${Math.min(budgetTotals.percent, 100)}%` }"
          />
        </div>
      </div>
      <table v-if="budgetRows.length" class="mt-4 w-full text-left text-xs">
        <caption class="sr-only">Category budget status</caption>
        <thead>
          <tr class="text-surface-mid">
            <th class="py-1 font-medium">category</th>
            <th class="py-1 font-medium text-right">spent</th>
            <th class="py-1 font-medium text-right">budget</th>
            <th class="py-1 font-medium text-right">%</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in budgetRows" :key="row.category" class="border-t border-surface-border/50">
            <td class="py-1.5 text-surface-light">{{ row.category }}</td>
            <td class="py-1.5 text-right font-data">{{ formatMoney(row.spent, currency) }}</td>
            <td class="py-1.5 text-right font-data">
              {{ formatMoney(row.budget ?? 0, currency) }}
            </td>
            <td
              class="py-1.5 text-right font-data"
              :class="row.overBudget ? 'text-status-error' : 'text-surface-mid'"
            >
              {{ row.percent }}%
            </td>
          </tr>
        </tbody>
      </table>
    </Card>

    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <Card>
        <h3 class="mb-3 text-xs text-surface-mid">monthly trend</h3>
        <ExpenseLineChart :labels="lineChart.labels" :values="lineChart.values" />
        <table class="mt-3 w-full text-left text-xs">
          <caption class="sr-only">Monthly totals</caption>
          <thead>
            <tr class="text-surface-mid">
              <th class="py-1 font-medium">period</th>
              <th class="py-1 font-medium text-right">total</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(label, i) in lineChart.labels"
              :key="label"
              class="border-t border-surface-border/50"
            >
              <td class="py-1.5 text-surface-light">{{ label }}</td>
              <td class="py-1.5 text-right font-data">
                {{ formatMoney(lineChart.values[i] ?? 0, currency) }}
              </td>
            </tr>
          </tbody>
        </table>
      </Card>

      <Card>
        <h3 class="mb-3 text-xs text-surface-mid">by category</h3>
        <ExpenseBarChart
          :labels="categorySeries.labels"
          :values="categorySeries.values"
          horizontal
        />
        <table class="mt-3 w-full text-left text-xs">
          <caption class="sr-only">Spend by category</caption>
          <thead>
            <tr class="text-surface-mid">
              <th class="py-1 font-medium">category</th>
              <th class="py-1 font-medium text-right">total</th>
              <th class="py-1 font-medium text-right">%</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in categorySeries.rows"
              :key="row.label"
              class="border-t border-surface-border/50"
            >
              <td class="py-1.5 text-surface-light">{{ row.label }}</td>
              <td class="py-1.5 text-right font-data">
                {{ formatMoney(row.value, currency) }}
              </td>
              <td class="py-1.5 text-right font-data text-surface-mid">{{ row.percent }}%</td>
            </tr>
          </tbody>
        </table>
      </Card>
    </div>

    <Card>
      <h3 class="mb-3 text-xs text-surface-mid">by product</h3>
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <ExpenseBarChart
          :labels="productSeries.labels"
          :values="productSeries.values"
          horizontal
        />
        <ExpenseDoughnutChart
          v-if="showProductDoughnut"
          :labels="productSeries.labels"
          :values="productSeries.values"
        />
      </div>
      <table class="mt-3 w-full text-left text-xs">
        <caption class="sr-only">Spend by product</caption>
        <thead>
          <tr class="text-surface-mid">
            <th class="py-1 font-medium">product</th>
            <th class="py-1 font-medium text-right">total</th>
            <th class="py-1 font-medium text-right">%</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in productSeries.rows"
            :key="row.label"
            class="border-t border-surface-border/50"
          >
            <td class="py-1.5 text-surface-light">{{ row.label }}</td>
            <td class="py-1.5 text-right font-data">
              {{ formatMoney(row.value, currency) }}
            </td>
            <td class="py-1.5 text-right font-data text-surface-mid">{{ row.percent }}%</td>
          </tr>
        </tbody>
      </table>
    </Card>
  </div>
  <EmptyState
    v-else
    title="No chart data yet"
    description="Add expenses for this period to see trends and breakdowns."
  >
    <template #action>
      <BaseButton variant="primary" size="sm" @click="emit('addExpense')">
        go to transactions
      </BaseButton>
    </template>
  </EmptyState>
</template>
