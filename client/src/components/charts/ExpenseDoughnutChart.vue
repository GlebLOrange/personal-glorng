<script setup lang="ts">
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from "chart.js";
import { computed } from "vue";
import { Doughnut } from "vue-chartjs";

import { CHART_COLORS, CHART_TEXT, chartDefaults } from "@/components/charts/chartTheme";

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps<{
  labels: string[];
  values: number[];
}>();

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      data: props.values,
      backgroundColor: props.labels.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]),
      borderColor: "#141820",
      borderWidth: 2,
    },
  ],
}));

const chartOptions = {
  ...chartDefaults,
  scales: undefined,
  plugins: {
    legend: {
      position: "right" as const,
      labels: { color: CHART_TEXT, font: { family: "Roboto Mono, monospace", size: 10 } },
    },
  },
};
</script>

<template>
  <div class="h-56">
    <Doughnut :data="chartData" :options="chartOptions" />
  </div>
</template>
