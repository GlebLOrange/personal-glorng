<script setup lang="ts">
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from "chart.js";
import { computed } from "vue";
import { Bar } from "vue-chartjs";

import { CHART_COLORS, chartDefaults } from "@/components/charts/chartTheme";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const props = defineProps<{
  labels: string[];
  values: number[];
}>();

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      label: "Total",
      data: props.values,
      backgroundColor: props.labels.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]),
    },
  ],
}));

const chartOptions = {
  ...chartDefaults,
  plugins: {
    ...chartDefaults.plugins,
    legend: { display: false },
  },
};
</script>

<template>
  <div class="h-56">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>
