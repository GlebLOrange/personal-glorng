<script setup lang="ts">
import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";
import { computed } from "vue";
import { Line } from "vue-chartjs";

import { CHART_COLORS, chartDefaults } from "@/components/charts/chartTheme";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const props = defineProps<{
  labels: string[];
  values: number[];
}>();

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      label: "Spending",
      data: props.values,
      borderColor: CHART_COLORS[0],
      backgroundColor: `${CHART_COLORS[0]}33`,
      tension: 0.3,
      fill: true,
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
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>
