/** Chart palette — hex mirrors @theme accents (canvas APIs need resolved colors). */
export const CHART_COLORS = [
  "#7bbde2", // --color-accent-blue
  "#b8a3c8", // --color-accent-violet
  "#d4ce94", // --color-accent-golden
  "#C4B8AC",
  "#8A847E",
  "#5a8fb0",
  "#9a87a8",
  "#a8a470",
] as const;

export const CHART_GRID = "#2e3a4e"; // --color-surface-border
export const CHART_TEXT = "#C4B8AC";

export const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: CHART_TEXT,
        font: { family: "IBM Plex Mono, ui-monospace, monospace", size: 11 },
      },
    },
  },
  scales: {
    x: {
      ticks: {
        color: CHART_TEXT,
        font: { family: "IBM Plex Mono, ui-monospace, monospace", size: 10 },
      },
      grid: { color: CHART_GRID },
    },
    y: {
      ticks: {
        color: CHART_TEXT,
        font: { family: "IBM Plex Mono, ui-monospace, monospace", size: 10 },
      },
      grid: { color: CHART_GRID },
    },
  },
};
