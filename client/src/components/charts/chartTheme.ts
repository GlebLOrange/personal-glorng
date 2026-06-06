export const CHART_COLORS = [
  "#7BBDE2",
  "#B8A3C8",
  "#D4CE94",
  "#C4B8AC",
  "#8A847E",
  "#5a8fb0",
  "#9a87a8",
  "#a8a470",
] as const;

export const CHART_GRID = "#2e3a4e";
export const CHART_TEXT = "#C4B8AC";

export const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: CHART_TEXT, font: { family: "IBM Plex Mono, ui-monospace, monospace", size: 11 } },
    },
  },
  scales: {
    x: {
      ticks: { color: CHART_TEXT, font: { family: "IBM Plex Mono, ui-monospace, monospace", size: 10 } },
      grid: { color: CHART_GRID },
    },
    y: {
      ticks: { color: CHART_TEXT, font: { family: "IBM Plex Mono, ui-monospace, monospace", size: 10 } },
      grid: { color: CHART_GRID },
    },
  },
};
