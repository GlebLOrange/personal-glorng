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

import { resolveChartTheme } from "@/components/charts/chartTheme";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const props = defineProps<{
  labels: string[];
  values: number[];
}>();

const theme = computed(() => resolveChartTheme());

const chartData = computed(() => {
  const color = theme.value.colors[0] ?? "#8ec4e0";
  return {
    labels: props.labels,
    datasets: [
      {
        label: "Spending",
        data: props.values,
        borderColor: color,
        backgroundColor: `${color}33`,
        tension: 0.3,
        fill: true,
      },
    ],
  };
});

const chartOptions = computed(() => {
  const { defaults } = theme.value;
  return {
    ...defaults,
    plugins: {
      ...defaults.plugins,
      legend: { display: false },
    },
  };
});
</script>

<template>
  <div class="h-56">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>
