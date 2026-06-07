<script setup lang="ts">
import ExpenseBarChart from "@/components/charts/ExpenseBarChart.vue";
import ExpenseDoughnutChart from "@/components/charts/ExpenseDoughnutChart.vue";
import ExpenseLineChart from "@/components/charts/ExpenseLineChart.vue";
import BaseCard from "@/components/ui/BaseCard.vue";

defineProps<{
  hasChartData: boolean;
  lineChart: { labels: string[]; values: number[] };
  barChart: { labels: string[]; values: number[] };
  doughnutChart: { labels: string[]; values: number[] };
}>();
</script>

<template>
  <div v-if="hasChartData" class="grid grid-cols-1 lg:grid-cols-3 gap-4">
    <BaseCard>
      <h3 class="text-xs text-surface-mid uppercase tracking-wider mb-3">Monthly trend</h3>
      <ExpenseLineChart :labels="lineChart.labels" :values="lineChart.values" />
    </BaseCard>
    <BaseCard>
      <h3 class="text-xs text-surface-mid uppercase tracking-wider mb-3">By category</h3>
      <ExpenseBarChart :labels="barChart.labels" :values="barChart.values" />
    </BaseCard>
    <BaseCard>
      <h3 class="text-xs text-surface-mid uppercase tracking-wider mb-3">By product</h3>
      <ExpenseDoughnutChart :labels="doughnutChart.labels" :values="doughnutChart.values" />
    </BaseCard>
  </div>
  <p v-else class="text-surface-mid text-sm text-center py-8">No chart data for this period yet.</p>
</template>
