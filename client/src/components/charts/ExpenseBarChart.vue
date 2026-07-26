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

import { resolveChartTheme } from "@/components/charts/chartTheme";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const props = withDefaults(
  defineProps<{
    labels: string[];
    values: number[];
    horizontal?: boolean;
  }>(),
  { horizontal: false },
);

const theme = computed(() => resolveChartTheme());

const chartData = computed(() => {
  const { colors } = theme.value;
  return {
    labels: props.labels,
    datasets: [
      {
        label: "Total",
        data: props.values,
        backgroundColor: props.labels.map((_, i) => colors[i % colors.length]),
      },
    ],
  };
});

const chartOptions = computed(() => {
  const { defaults } = theme.value;
  return {
    ...defaults,
    indexAxis: props.horizontal ? ("y" as const) : ("x" as const),
    plugins: {
      ...defaults.plugins,
      legend: { display: false },
    },
  };
});
</script>

<template>
  <div class="h-56">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>
