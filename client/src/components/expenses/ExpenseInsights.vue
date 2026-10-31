<script setup lang="ts">
import { computed, defineAsyncComponent } from "vue";

import ExpenseCategoryBreakdown from "@/components/expenses/ExpenseCategoryBreakdown.vue";
import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card } from "@/components/ui/card";
import type { ExpenseSummary } from "@/types";

const ExpenseBarChart = defineAsyncComponent(
  () => import("@/components/charts/ExpenseBarChart.vue"),
);
const ExpenseDoughnutChart = defineAsyncComponent(
  () => import("@/components/charts/ExpenseDoughnutChart.vue"),
);
const ExpenseLineChart = defineAsyncComponent(
  () => import("@/components/charts/ExpenseLineChart.vue"),
);

const props = defineProps<{
  hasChartData: boolean;
  lineChart: { labels: string[]; values: number[] };
  barChart: { labels: string[]; values: number[] };
  doughnutChart: { labels: string[]; values: number[] };
  summary: ExpenseSummary | null;
  formatMoney: (amount: string | number, currency: string) => string;
}>();

const emit = defineEmits<{
  addExpense: [];
}>();

const MAX_SERIES = 6;

function foldSeries(
  labels: string[],
  values: number[],
): {
  labels: string[];
  values: number[];
  rows: Array<{ label: string; value: number; percent: number }>;
} {
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

const categorySeries = computed(() => foldSeries(props.barChart.labels, props.barChart.values));
const productSeries = computed(() =>
  foldSeries(props.doughnutChart.labels, props.doughnutChart.values),
);

const showProductDoughnut = computed(
  () => productSeries.value.labels.length > 0 && productSeries.value.labels.length <= 5,
);

const currency = computed(() => props.summary?.currency ?? "PLN");
</script>

<template>
  <div v-if="hasChartData" class="flex flex-col gap-3">
    <ExpenseCategoryBreakdown :summary="summary" :format-money="formatMoney" />

    <div class="grid grid-cols-1 gap-3 lg:grid-cols-2">
      <Card variant="compact">
        <h3 class="mb-3 text-sm font-semibold text-surface-light">monthly trend</h3>
        <ExpenseLineChart :labels="lineChart.labels" :values="lineChart.values" />
        <details class="mt-3 group">
          <summary
            class="cursor-pointer list-none text-xs text-surface-mid marker:content-none [&::-webkit-details-marker]:hidden"
          >
            <span class="underline-offset-2 group-open:underline">data table</span>
          </summary>
          <table class="mt-2 w-full text-left text-xs">
            <caption class="sr-only">
              Monthly totals
            </caption>
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
        </details>
      </Card>

      <Card variant="compact">
        <h3 class="mb-3 text-sm font-semibold text-surface-light">by category</h3>
        <ExpenseBarChart
          :labels="categorySeries.labels"
          :values="categorySeries.values"
          horizontal
        />
        <details class="mt-3 group">
          <summary
            class="cursor-pointer list-none text-xs text-surface-mid marker:content-none [&::-webkit-details-marker]:hidden"
          >
            <span class="underline-offset-2 group-open:underline">data table</span>
          </summary>
          <table class="mt-2 w-full text-left text-xs">
            <caption class="sr-only">
              Spend by category
            </caption>
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
        </details>
      </Card>
    </div>

    <Card variant="compact">
      <h3 class="mb-3 text-sm font-semibold text-surface-light">by product</h3>
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <ExpenseBarChart :labels="productSeries.labels" :values="productSeries.values" horizontal />
        <ExpenseDoughnutChart
          v-if="showProductDoughnut"
          :labels="productSeries.labels"
          :values="productSeries.values"
        />
      </div>
      <details class="mt-3 group">
        <summary
          class="cursor-pointer list-none text-xs text-surface-mid marker:content-none [&::-webkit-details-marker]:hidden"
        >
          <span class="underline-offset-2 group-open:underline">data table</span>
        </summary>
        <table class="mt-2 w-full text-left text-xs">
          <caption class="sr-only">
            Spend by product
          </caption>
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
      </details>
    </Card>
  </div>
  <EmptyState
    v-else
    title="no chart data yet"
    description="add expenses for this period to see trends and breakdowns."
  >
    <template #action>
      <BaseButton
        variant="ghost"
        size="sm"
        class="gap-1.5"
        @click="emit('addExpense')"
      >
        <ChevronIcon class-name="size-3.5 shrink-0" />
        go to today
      </BaseButton>
    </template>
  </EmptyState>
</template>
