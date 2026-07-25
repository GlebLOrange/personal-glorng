/** Chart palette — hex mirrors @theme 1xx–5xx families (canvas APIs need resolved colors). */
export const CHART_COLORS = [
  "#8ec4e0", // --color-accent-blue (1xx)
  "#7bc49a", // --color-status-success (2xx)
  "#7eb8b0", // --color-status-cyan (3xx)
  "#e88a8a", // --color-status-error (4xx)
  "#d98aad", // --color-status-critical (5xx)
  "#d4cdc6", // --color-surface-mid
  "#a39d97", // --color-surface-muted
  "#6b7a90", // --color-surface-border
] as const;

/** Darker mix for grid lines — border token is too light on canvas. */
export const CHART_GRID = "#2e3a4e";
export const CHART_TEXT = "#d4cdc6"; // --color-surface-mid

export const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: CHART_TEXT,
        font: { family: "IBM Plex Sans, Segoe UI, system-ui, sans-serif", size: 11 },
      },
    },
  },
  scales: {
    x: {
      ticks: {
        color: CHART_TEXT,
        font: { family: "IBM Plex Sans, Segoe UI, system-ui, sans-serif", size: 10 },
      },
      grid: { color: CHART_GRID },
    },
    y: {
      ticks: {
        color: CHART_TEXT,
        font: { family: "IBM Plex Sans, Segoe UI, system-ui, sans-serif", size: 10 },
      },
      grid: { color: CHART_GRID },
    },
  },
};
