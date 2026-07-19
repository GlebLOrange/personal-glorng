<script setup lang="ts">
import { computed } from "vue";

import ExpenseBarChart from "@/components/charts/ExpenseBarChart.vue";
import ExpenseDoughnutChart from "@/components/charts/ExpenseDoughnutChart.vue";
import ExpenseLineChart from "@/components/charts/ExpenseLineChart.vue";
import { Card } from "@/components/ui/card";

const props = defineProps<{
  hasChartData: boolean;
  lineChart: { labels: string[]; values: number[] };
  barChart: { labels: string[]; values: number[] };
  doughnutChart: { labels: string[]; values: number[] };
}>();

function chartSummary(labels: string[], values: number[]): string {
  if (!labels.length || !values.length) return "No data";
  const total = values.reduce((sum, n) => sum + n, 0);
  const topIdx = values.indexOf(Math.max(...values));
  const topLabel = labels[topIdx] ?? "n/a";
  return `Total ${total.toFixed(2)}; highest ${topLabel} at ${(values[topIdx] ?? 0).toFixed(2)}`;
}

const lineSummary = computed(() => chartSummary(props.lineChart.labels, props.lineChart.values));
const barSummary = computed(() => chartSummary(props.barChart.labels, props.barChart.values));
const doughnutSummary = computed(() =>
  chartSummary(props.doughnutChart.labels, props.doughnutChart.values),
);
</script>

<template>
  <div v-if="hasChartData" class="grid grid-cols-1 lg:grid-cols-3 gap-4">
    <Card>
      <h3 class="text-xs text-surface-mid uppercase tracking-wider mb-3">Monthly trend</h3>
      <ExpenseLineChart :labels="lineChart.labels" :values="lineChart.values" />
      <p class="sr-only">{{ lineSummary }}</p>
    </Card>
    <Card>
      <h3 class="text-xs text-surface-mid uppercase tracking-wider mb-3">By category</h3>
      <ExpenseBarChart :labels="barChart.labels" :values="barChart.values" />
      <p class="sr-only">{{ barSummary }}</p>
    </Card>
    <Card>
      <h3 class="text-xs text-surface-mid uppercase tracking-wider mb-3">By product</h3>
      <ExpenseDoughnutChart :labels="doughnutChart.labels" :values="doughnutChart.values" />
      <p class="sr-only">{{ doughnutSummary }}</p>
    </Card>
  </div>
  <p v-else class="text-surface-mid text-sm text-center py-8">No chart data for this period yet.</p>
</template>
