<script setup lang="ts">
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from "chart.js";
import { computed } from "vue";
import { Doughnut } from "vue-chartjs";

import { resolveChartTheme } from "@/components/charts/chartTheme";

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps<{
  labels: string[];
  values: number[];
}>();

const theme = computed(() => resolveChartTheme());

const chartData = computed(() => {
  const { colors } = theme.value;
  return {
    labels: props.labels,
    datasets: [
      {
        data: props.values,
        backgroundColor: props.labels.map((_, i) => colors[i % colors.length]),
        borderColor: "#141820",
        borderWidth: 2,
      },
    ],
  };
});

const chartOptions = computed(() => {
  const { text } = theme.value;
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "right" as const,
        labels: {
          color: text,
          font: { family: "IBM Plex Sans, Segoe UI, system-ui, sans-serif", size: 10 },
        },
      },
    },
  };
});
</script>

<template>
  <div class="h-56">
    <Doughnut :data="chartData" :options="chartOptions" />
  </div>
</template>
